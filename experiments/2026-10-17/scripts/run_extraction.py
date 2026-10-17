"""Phase 2 extraction runner for the 2026-10-17 v0.9 field experiment.

Usage (repo root; keys from .env):
  python -P experiments/2026-10-17/scripts/run_extraction.py --pilot            # 3 texts x all extractors x 1 repeat -> raw/pilot/
  python -P experiments/2026-10-17/scripts/run_extraction.py                    # full run, resumes from raw/<model>/<arm>.jsonl
  python -P experiments/2026-10-17/scripts/run_extraction.py --models claude-haiku-5-5 --arms synthetic --repeats 2

Every call is checkpointed to experiments/2026-10-17/raw/<model>/<arm>.jsonl before the next call on that file is issued;
(text_id, repeat) pairs already present are never re-requested. Spend is accumulated from each response's usage at the
pinned list prices (models.json) and written to spend.json; the projection (spent + remaining calls x mean cost so far)
is checked before the run and after every 500 completed calls. If the projected extraction total plus the judge / rater
reserves exceeds the budget the run stops and STATUS.md is written.
"""
import argparse, asyncio, json, os, sys, time, hashlib, random, traceback
from collections import defaultdict
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(EXP))
load_dotenv(os.path.join(ROOT, '.env'))
MODELS = json.load(open(os.path.join(EXP, 'models.json'), encoding='utf-8'))
PROMPTS = {n: open(os.path.join(EXP, 'prompts', f'{n}.txt'), encoding='utf-8').read() for n in ('extraction_system', 'extraction_user')}
RAW = os.path.join(EXP, 'raw')
BUDGET = MODELS['budget_usd']
RESERVE = {'judge': 16.0, 'rater': 5.0}  # pre-registered reserves (experiment-plan.md section 8); re-estimated in STATUS/RESULTS

def load_texts():
    rows = [json.loads(l) for l in open(os.path.join(EXP, 'corpus', '.resolved_texts.jsonl'), encoding='utf-8')]
    return {r['id']: r for r in rows}

def price_of(model_entry, usage):
    p = model_entry['price']
    inp, cached, cw, out = usage.get('input_tokens', 0), usage.get('cached_input_tokens', 0), usage.get('cache_write_tokens', 0), usage.get('output_tokens', 0)
    return (inp * p['input'] + cached * p['cached_input'] + cw * p.get('cache_write', p['input']) + out * p['output']) / 1e6

def parse_json(text):
    t = text.strip()
    if t.startswith('```'):
        t = t.split('\n', 1)[1] if '\n' in t else t[3:]
        if t.rstrip().endswith('```'): t = t.rstrip()[:-3]
    a, b = t.find('{'), t.rfind('}')
    if a < 0 or b < 0: raise ValueError('no JSON object')
    return json.loads(t[a:b + 1])

class Provider:
    def __init__(self, entry):
        self.entry = entry; self.model = entry['model']; self.kind = entry['provider']
        if self.kind == 'anthropic':
            import anthropic
            self.client = anthropic.AsyncAnthropic(timeout=600.0, max_retries=3)
        else:
            from openai import AsyncOpenAI
            key = os.environ[MODELS['env_keys'][self.kind]]
            self.client = AsyncOpenAI(api_key=key, base_url=entry.get('base_url'), timeout=600.0, max_retries=3)

    async def call(self, system, user):
        if self.kind == 'anthropic':
            r = await self.client.messages.create(
                model=self.model, max_tokens=16000,
                system=[{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}],  # 5-minute TTL: write 1.25 x input, matches models.json
                messages=[{'role': 'user', 'content': user}])
            text = ''.join(b.text for b in r.content if b.type == 'text')
            u = r.usage
            usage = {'input_tokens': u.input_tokens, 'output_tokens': u.output_tokens,
                     'cached_input_tokens': getattr(u, 'cache_read_input_tokens', 0) or 0, 'cache_write_tokens': getattr(u, 'cache_creation_input_tokens', 0) or 0}
            return text, usage, r.stop_reason, r.model
        kwargs = dict(model=self.model, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                      response_format={'type': 'json_object'})
        if self.kind == 'openai': kwargs['max_completion_tokens'] = 16000
        else:
            kwargs['max_tokens'] = 12000
            # Deviation D1 (experiment-plan.md section 10, logged before the main run): kimi-k2.6 is a reasoning model whose
            # default reasoning (~10k tokens, 126 s per call in the pilot probe) exceeded the output cap and pushed the projected
            # total above USD 80; thinking is disabled for this extractor. Sampling parameters remain provider defaults.
            kwargs['extra_body'] = {'thinking': {'type': 'disabled'}}
        r = await self.client.chat.completions.create(**kwargs)
        ch = r.choices[0]
        text = ch.message.content or ''
        u = r.usage
        cached = 0
        det = getattr(u, 'prompt_tokens_details', None)
        if det is not None: cached = getattr(det, 'cached_tokens', 0) or 0
        usage = {'input_tokens': (u.prompt_tokens or 0) - cached, 'output_tokens': u.completion_tokens or 0, 'cached_input_tokens': cached, 'cache_write_tokens': 0}
        return text, usage, ch.finish_reason, r.model

class Checkpoint:
    def __init__(self, path):
        self.path = path; self.done = {}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            for l in open(path, encoding='utf-8'):
                if l.strip():
                    rec = json.loads(l); self.done[(rec['text_id'], rec['repeat'])] = rec
    def append(self, rec):
        with open(self.path, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
        self.done[(rec['text_id'], rec['repeat'])] = rec

class Spend:
    def __init__(self, path):
        self.path = path
        self.data = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {'by_model': {}, 'total_usd': 0.0, 'calls': 0}
    def add(self, model, cost, usage):
        m = self.data['by_model'].setdefault(model, {'usd': 0.0, 'calls': 0, 'input_tokens': 0, 'cached_input_tokens': 0, 'cache_write_tokens': 0, 'output_tokens': 0})
        m['usd'] += cost; m['calls'] += 1
        for k in ('input_tokens', 'cached_input_tokens', 'cache_write_tokens', 'output_tokens'): m[k] += usage.get(k, 0)
        self.data['total_usd'] += cost; self.data['calls'] += 1
        json.dump(self.data, open(self.path, 'w', encoding='utf-8'), indent=1)

def write_status(reason, extra=None):
    p = os.path.join(EXP, 'STATUS.md')
    body = f"# STATUS (written by run_extraction.py at {time.strftime('%Y-%m-%d %H:%M:%S')})\n\n**Run stopped.** {reason}\n\n"
    if extra: body += '```json\n' + json.dumps(extra, indent=1) + '\n```\n'
    open(p, 'w', encoding='utf-8', newline='\n').write(body)
    print('STATUS.md written:', reason)

async def worker(prov, jobs, ck, spend, sem, texts, system, stats, label):
    for text_id, repeat in jobs:
        if (text_id, repeat) in ck.done: continue
        user = PROMPTS['extraction_user'].format(text_id=text_id, text=texts[text_id]['text'])
        req_sha = hashlib.sha256((prov.model + '\n' + system + '\n' + user).encode('utf-8')).hexdigest()
        attempt, delay = 0, 5
        while True:
            attempt += 1
            t0 = time.time()
            try:
                async with sem:
                    raw, usage, stop, served = await prov.call(system, user)
                break
            except Exception as e:  # transport / rate-limit after SDK retries: back off and retry; model output is never re-sampled
                msg = repr(e)[:300]
                if attempt >= 6:
                    rec = {'text_id': text_id, 'repeat': repeat, 'model': prov.model, 'provider': prov.kind, 'request_sha256': req_sha, 'ts': time.time(),
                           'latency_s': round(time.time() - t0, 2), 'usage': None, 'cost_usd': 0.0, 'raw_text': None, 'parsed': None,
                           'parse_error': None, 'transport_error': msg, 'stop_reason': None}
                    ck.append(rec); stats['transport_fail'] += 1
                    print(f'  [{label}] {text_id} r{repeat} TRANSPORT FAIL after {attempt} attempts: {msg}')
                    break
                await asyncio.sleep(delay + random.random() * 2); delay = min(delay * 2, 120)
                continue
        else:
            continue
        if attempt >= 6 and (text_id, repeat) in ck.done: continue
        cost = price_of(prov.entry, usage)
        parsed, perr = None, None
        try: parsed = parse_json(raw)
        except Exception as e: perr = repr(e)[:200]
        rec = {'text_id': text_id, 'repeat': repeat, 'model': prov.model, 'served_model': served, 'provider': prov.kind, 'request_sha256': req_sha, 'ts': time.time(),
               'latency_s': round(time.time() - t0, 2), 'usage': usage, 'cost_usd': round(cost, 6), 'raw_text': raw, 'parsed': parsed,
               'parse_error': perr, 'transport_error': None, 'stop_reason': stop}
        ck.append(rec); spend.add(prov.model, cost, usage)
        stats['calls'] += 1; stats['usd'] += cost
        if perr: stats['parse_fail'] += 1
        if stats['calls'] % 25 == 0:
            print(f"  [{label}] {stats['calls']} calls, ${stats['usd']:.2f} this run, total ${spend.data['total_usd']:.2f}, parse_fail={stats['parse_fail']}")
        if stats['calls'] % 500 == 0:
            proj = project(spend, stats)
            print(f'  projection after {stats["calls"]} calls: {json.dumps(proj)}')
            if proj['projected_total_usd'] > BUDGET:
                write_status(f"projected total USD {proj['projected_total_usd']:.2f} exceeds budget USD {BUDGET} after {stats['calls']} calls", proj)
                stats['abort'] = True
        if stats.get('abort'): return

def project(spend, stats):
    remaining = stats['planned'] - sum(m['calls'] for m in spend.data['by_model'].values() if m['calls'])
    remaining = max(0, remaining)
    mean_cost = (spend.data['total_usd'] / spend.data['calls']) if spend.data['calls'] else 0.0
    ext = spend.data['total_usd'] + remaining * mean_cost
    return {'spent_usd': round(spend.data['total_usd'], 2), 'completed_calls': spend.data['calls'], 'remaining_calls': remaining, 'mean_cost_per_call_usd': round(mean_cost, 4),
            'projected_extraction_usd': round(ext, 2), 'reserves_usd': RESERVE, 'projected_total_usd': round(ext + sum(RESERVE.values()), 2), 'budget_usd': BUDGET}

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true'); ap.add_argument('--models', default=None); ap.add_argument('--arms', default='synthetic,conversational,pepys')
    ap.add_argument('--repeats', type=int, default=5); ap.add_argument('--concurrency', type=int, default=6); ap.add_argument('--pilot-n', type=int, default=3)
    a = ap.parse_args()
    texts = load_texts()
    extractors = [e for e in MODELS['extractors'].values() if not a.models or e['model'] in a.models.split(',')]
    arms = a.arms.split(',')
    system = PROMPTS['extraction_system']
    ids_by_arm = defaultdict(list)
    for tid, r in texts.items(): ids_by_arm[r['arm']].append(tid)
    for k in ids_by_arm: ids_by_arm[k].sort()
    if a.pilot:
        rng = random.Random(7)
        pilot_ids = [rng.choice(ids_by_arm[arm]) for arm in arms][:a.pilot_n]
        plan = {e['model']: {'pilot': [(t, 1) for t in pilot_ids]} for e in extractors}
        raw_dir = os.path.join(RAW, 'pilot'); spend_path = os.path.join(EXP, 'spend_pilot.json')
    else:
        plan = {e['model']: {arm: [(t, r) for t in ids_by_arm[arm] for r in range(1, a.repeats + 1)] for arm in arms} for e in extractors}
        raw_dir = RAW; spend_path = os.path.join(EXP, 'spend.json')
    spend = Spend(spend_path)
    planned = sum(len(j) for m in plan.values() for j in m.values())
    stats = {'calls': 0, 'usd': 0.0, 'parse_fail': 0, 'transport_fail': 0, 'planned': planned}
    if not a.pilot:
        proj = project(spend, stats); print('projection before run:', json.dumps(proj))
        if spend.data['calls'] and proj['projected_total_usd'] > BUDGET:
            write_status(f"projected total USD {proj['projected_total_usd']:.2f} exceeds budget USD {BUDGET} before run", proj); return 2
    tasks = []
    for e in extractors:
        prov = Provider(e); sem = asyncio.Semaphore(a.concurrency if e['provider'] != 'kimi' else max(2, a.concurrency // 2))
        for arm, jobs in plan[e['model']].items():
            ck = Checkpoint(os.path.join(raw_dir, e['model'] if not a.pilot else '', f'{arm}.jsonl') if not a.pilot else os.path.join(raw_dir, f"{e['model']}.jsonl"))
            todo = [j for j in jobs if j not in ck.done]
            print(f"{e['model']} / {arm}: {len(jobs)} planned, {len(todo)} to do")
            # split the job list into `concurrency` interleaved lanes sharing one semaphore and one checkpoint file
            lanes = max(1, min(a.concurrency, len(todo)))
            for i in range(lanes):
                tasks.append(worker(prov, todo[i::lanes], ck, spend, sem, texts, system, stats, f"{e['model']}/{arm}"))
    t0 = time.time()
    await asyncio.gather(*tasks)
    print(f"done in {time.time() - t0:.0f}s: {stats['calls']} calls, ${stats['usd']:.2f} this run; cumulative ${spend.data['total_usd']:.2f}; parse_fail={stats['parse_fail']} transport_fail={stats['transport_fail']}")
    print('final projection:', json.dumps(project(spend, stats)))
    return 1 if stats.get('abort') else 0

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
