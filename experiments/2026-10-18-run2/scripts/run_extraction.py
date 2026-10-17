"""Run-2 extraction runner (experiment-plan-run2.md sections 2-4, 9): 150 texts x 5 repeats x 2 prompt arms (A = v0.8.3 text,
B = v0.9 definitions) x 5 extractors, checkpointed to raw/<model>/<A|B>/<corpus_arm>.jsonl; (text_id, repeat, prompt_arm)
already present are never re-requested. Spend at the pinned list prices (models.json) -> spend.json; projection checked
before the run and every 1,000 calls against the USD 60 hard stop (judge reserve 18). Pilot gate levers in order: drop
gpt-5.4-mini; Claude effort low; do not start.

Usage (repo root; keys from .env):
  python -P experiments/2026-10-18-run2/scripts/run_extraction.py --pilot                 # 3 texts x 5 extractors x 2 arms -> raw/pilot/
  python -P experiments/2026-10-18-run2/scripts/run_extraction.py                         # full run, resumes
  python -P experiments/2026-10-18-run2/scripts/run_extraction.py --models gpt-5.4-mini   # one extractor
"""
import argparse, asyncio, json, os, sys, time, hashlib, random
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP); ROOT = os.path.dirname(EXPS)
RUN1 = os.path.join(EXPS, '2026-10-17')
sys.path.insert(0, os.path.join(RUN1, 'scripts'))
from run_extraction import Provider, Spend, Checkpoint, price_of, parse_json  # noqa: E402  (run-1 helpers, unchanged)

MODELS = json.load(open(os.path.join(EXP, 'models.json'), encoding='utf-8'))
BUDGET = MODELS['budget_usd']; RESERVE = {'judge': 18.0}
PROMPTS = {n: open(os.path.join(EXP, 'prompts', f'{n}.txt'), encoding='utf-8').read() for n in ('arm_a_system', 'arm_b_system', 'extraction_user')}
SYSTEM = {'A': PROMPTS['arm_a_system'], 'B': PROMPTS['arm_b_system']}
RAW = os.path.join(EXP, 'raw')
KEYS = {'A': ['anchor', 'spark', 'wound', 'fuel', 'bridge', 'echo', 'narrative'], 'B': ['subject', 'trigger', 'harm', 'drive', 'integration', 'retrieval_cues', 'summary']}
SLOTS = ['subject', 'trigger', 'harm', 'drive', 'integration', 'retrieval_cues', 'summary']  # canonical ids; Arm A keys map by position
CORPUS_ARMS = ('synthetic', 'conversational', 'pepys')


def load_texts():
    """run-1 resolved texts (never committed), verified against the run-2 manifest sha256 per text; mismatch aborts."""
    man = {}
    for l in open(os.path.join(EXP, 'corpus', 'corpus_manifest.jsonl'), encoding='utf-8'):
        if l.strip(): r = json.loads(l); man[r['id']] = r
    rows = {}
    for l in open(os.path.join(RUN1, 'corpus', '.resolved_texts.jsonl'), encoding='utf-8'):
        r = json.loads(l); rows[r['id']] = r
    if set(rows) != set(man): raise SystemExit('corpus id set differs from the run-2 manifest')
    for tid, r in rows.items():
        if hashlib.sha256(r['text'].encode('utf-8')).hexdigest() != man[tid]['sha256']: raise SystemExit(f'sha256 mismatch for {tid}; run aborted')
        r['arm'] = man[tid]['arm']
    return rows


def canon(parsed, arm):
    """-> (dict keyed by canonical slot id, list of missing keys). Keys matched case-insensitively, dotted prefixes dropped."""
    if not isinstance(parsed, dict): return None, KEYS[arm]
    low = {}
    for k, v in parsed.items():
        kk = str(k).strip().lower().split('.')[-1]
        low.setdefault(kk, v)
    out = {}; missing = []
    for slot, key in zip(SLOTS, KEYS[arm]):
        if key in low: out[slot] = low[key]
        else: out[slot] = None; missing.append(key)
    if arm == 'B':  # shape coercion for the list slot (plan section 11.1)
        v = out['retrieval_cues']
        if v is None: out['retrieval_cues'] = []
        elif isinstance(v, str): out['retrieval_cues'] = [v] if v.strip() else []
        elif not isinstance(v, list): out['retrieval_cues'] = [str(v)]
    return out, missing


class Provider2(Provider):
    """run-1 provider with the optional Claude effort lever (pilot gate lever 2; logged as a deviation when used)."""
    def __init__(self, entry, effort=None):
        super().__init__(entry); self.effort = effort

    async def call(self, system, user):
        if self.kind == 'anthropic' and self.effort:
            r = await self.client.messages.create(model=self.model, max_tokens=16000, output_config={'effort': self.effort},
                                                  system=[{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}],
                                                  messages=[{'role': 'user', 'content': user}])
            text = ''.join(b.text for b in r.content if b.type == 'text'); u = r.usage
            usage = {'input_tokens': u.input_tokens, 'output_tokens': u.output_tokens, 'cached_input_tokens': getattr(u, 'cache_read_input_tokens', 0) or 0, 'cache_write_tokens': getattr(u, 'cache_creation_input_tokens', 0) or 0}
            return text, usage, r.stop_reason, r.model
        return await super().call(system, user)


class Checkpoint2(Checkpoint):
    def __init__(self, path):
        self.path = path; self.done = {}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            for l in open(path, encoding='utf-8'):
                if l.strip():
                    rec = json.loads(l); self.done[(rec['text_id'], rec['repeat'])] = rec


async def worker(prov, arm, jobs, ck, spend, sem, texts, stats, label):
    system = SYSTEM[arm]
    for text_id, repeat in jobs:
        if (text_id, repeat) in ck.done: continue
        user = PROMPTS['extraction_user'].format(text_id=text_id, text=texts[text_id]['text'])
        req_sha = hashlib.sha256((prov.model + '\n' + system + '\n' + user).encode('utf-8')).hexdigest()
        attempt, delay = 0, 5; t0 = time.time()
        while True:
            attempt += 1; t0 = time.time()
            try:
                async with sem:
                    raw, usage, stop, served = await prov.call(system, user)
                break
            except Exception as e:
                msg = repr(e)[:300]
                if attempt >= 6:
                    ck.append({'text_id': text_id, 'repeat': repeat, 'prompt_arm': arm, 'model': prov.model, 'provider': prov.kind, 'request_sha256': req_sha, 'ts': time.time(),
                               'latency_s': round(time.time() - t0, 2), 'usage': None, 'cost_usd': 0.0, 'raw_text': None, 'parsed': None, 'canon': None, 'missing_keys': None,
                               'parse_error': None, 'transport_error': msg, 'stop_reason': None})
                    stats['transport_fail'] += 1; print(f'  [{label}] {text_id} r{repeat} TRANSPORT FAIL after {attempt} attempts: {msg}')
                    break
                await asyncio.sleep(delay + random.random() * 2); delay = min(delay * 2, 120)
                continue
        if (text_id, repeat) in ck.done: continue
        cost = price_of(prov.entry, usage)
        parsed, perr, cn, missing = None, None, None, None
        try: parsed = parse_json(raw); cn, missing = canon(parsed, arm)
        except Exception as e: perr = repr(e)[:200]
        rec = {'text_id': text_id, 'repeat': repeat, 'prompt_arm': arm, 'model': prov.model, 'served_model': served, 'provider': prov.kind, 'request_sha256': req_sha, 'ts': time.time(),
               'latency_s': round(time.time() - t0, 2), 'usage': usage, 'cost_usd': round(cost, 6), 'raw_text': raw, 'parsed': parsed, 'canon': cn, 'missing_keys': missing,
               'parse_error': perr, 'transport_error': None, 'stop_reason': stop}
        ck.append(rec); spend.add(prov.model, cost, usage)
        stats['calls'] += 1; stats['usd'] += cost
        if perr: stats['parse_fail'] += 1
        if missing: stats['missing_keys'] += 1
        if stats['calls'] % 50 == 0:
            print(f"  [{label}] {stats['calls']} calls, ${stats['usd']:.2f} this run, total ${spend.data['total_usd']:.2f}, parse_fail={stats['parse_fail']} missing_keys={stats['missing_keys']}")
        if stats['calls'] % 1000 == 0:
            proj = project(spend, stats); print(f'  projection after {stats["calls"]} calls: {json.dumps(proj)}')
            if proj['projected_total_usd'] > BUDGET:
                write_status(f"projected total USD {proj['projected_total_usd']:.2f} exceeds the USD {BUDGET} hard stop after {stats['calls']} calls", proj); stats['abort'] = True
        if stats.get('abort'): return


def project(spend, stats):
    """projected total = spent + sum over models of (remaining calls x that model's mean cost so far) + judge reserve."""
    ext = spend.data['total_usd']
    for model, planned in stats['planned_by_model'].items():
        m = spend.data['by_model'].get(model)
        done = m['calls'] if m else 0; mean = (m['usd'] / m['calls']) if m and m['calls'] else stats['pilot_mean'].get(model, 0.0)
        ext += max(0, planned - done) * mean
    return {'spent_usd': round(spend.data['total_usd'], 2), 'completed_calls': spend.data['calls'], 'projected_extraction_usd': round(ext, 2), 'reserves_usd': RESERVE,
            'projected_total_usd': round(ext + sum(RESERVE.values()), 2), 'budget_usd': BUDGET}


def write_status(reason, extra=None):
    p = os.path.join(EXP, 'STATUS.md')
    body = f"# STATUS (written by run_extraction.py at {time.strftime('%Y-%m-%d %H:%M:%S')})\n\n**Run stopped.** {reason}\n\n"
    if extra: body += '```json\n' + json.dumps(extra, indent=1) + '\n```\n'
    open(p, 'w', encoding='utf-8', newline='\n').write(body); print('STATUS.md written:', reason)


def pilot_means():
    """mean cost per call per model from raw/pilot/*.jsonl (for the projection before the main run)."""
    out = {}
    pd = os.path.join(RAW, 'pilot')
    if not os.path.isdir(pd): return out
    for f in os.listdir(pd):
        if not f.endswith('.jsonl'): continue
        costs = [json.loads(l)['cost_usd'] for l in open(os.path.join(pd, f), encoding='utf-8') if l.strip()]
        if costs: out[f[:-6]] = sum(costs) / len(costs)
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true'); ap.add_argument('--models', default=None); ap.add_argument('--arms', default='A,B'); ap.add_argument('--corpus', default=','.join(CORPUS_ARMS))
    ap.add_argument('--repeats', type=int, default=5); ap.add_argument('--concurrency', type=int, default=8); ap.add_argument('--claude-effort', default=None)
    a = ap.parse_args()
    texts = load_texts()
    extractors = [e for e in MODELS['extractors'].values() if not a.models or e['model'] in a.models.split(',')]
    prompt_arms = a.arms.split(','); corpus_arms = a.corpus.split(',')
    ids_by_arm = defaultdict(list)
    for tid, r in texts.items(): ids_by_arm[r['arm']].append(tid)
    for k in ids_by_arm: ids_by_arm[k].sort()
    index_of = {tid: i for i, tid in enumerate(sorted(texts))}
    if a.pilot:
        rng = random.Random(7); pilot_ids = [rng.choice(ids_by_arm[arm]) for arm in CORPUS_ARMS]
        plan = {e['model']: {(arm, 'pilot'): [(t, 1) for t in pilot_ids] for arm in prompt_arms} for e in extractors}
        raw_dir = os.path.join(RAW, 'pilot'); spend = Spend(os.path.join(EXP, 'spend_pilot.json'))
    else:
        plan = {}
        for e in extractors:
            plan[e['model']] = {}
            for carm in corpus_arms:
                for parm in prompt_arms:
                    plan[e['model']][(parm, carm)] = [(t, r) for t in ids_by_arm[carm] for r in range(1, a.repeats + 1)]
        raw_dir = RAW; spend = Spend(os.path.join(EXP, 'spend.json'))
    stats = {'calls': 0, 'usd': 0.0, 'parse_fail': 0, 'transport_fail': 0, 'missing_keys': 0, 'pilot_mean': pilot_means(),
             'planned_by_model': {m: sum(len(j) for j in jobs.values()) for m, jobs in plan.items()}}
    if not a.pilot:
        proj = project(spend, stats); print('projection before run:', json.dumps(proj))
        if proj['projected_total_usd'] > BUDGET: write_status(f"projected total USD {proj['projected_total_usd']:.2f} exceeds the USD {BUDGET} hard stop before the run", proj); return 2
    tasks = []
    for e in extractors:
        prov = Provider2(e, a.claude_effort); sem = asyncio.Semaphore(a.concurrency if e['provider'] != 'kimi' else max(2, a.concurrency // 2))
        for (parm, carm), jobs in plan[e['model']].items():
            path = os.path.join(raw_dir, f"{e['model']}_{parm}.jsonl") if a.pilot else os.path.join(raw_dir, e['model'], parm, f'{carm}.jsonl')
            ck = Checkpoint2(path)
            todo = [j for j in jobs if j not in ck.done]
            # arm order alternated by text index parity (plan section 3): even-index texts run A before B, odd-index B before A;
            # implemented by reversing the lane order for the arm that goes second on each text
            if not a.pilot: todo.sort(key=lambda j: (j[0], j[1], 0 if (index_of[j[0]] % 2 == 0) == (parm == 'A') else 1))
            print(f"{e['model']} / {parm} / {carm}: {len(jobs)} planned, {len(todo)} to do")
            lanes = max(1, min(a.concurrency, len(todo)))
            for i in range(lanes): tasks.append(worker(prov, parm, todo[i::lanes], ck, spend, sem, texts, stats, f"{e['model']}/{parm}/{carm}"))
    t0 = time.time()
    await asyncio.gather(*tasks)
    print(f"done in {time.time() - t0:.0f}s: {stats['calls']} calls, ${stats['usd']:.2f} this run; cumulative ${spend.data['total_usd']:.2f}; parse_fail={stats['parse_fail']} missing_keys={stats['missing_keys']} transport_fail={stats['transport_fail']}")
    if not a.pilot: print('final projection:', json.dumps(project(spend, stats)))
    return 1 if stats.get('abort') else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
