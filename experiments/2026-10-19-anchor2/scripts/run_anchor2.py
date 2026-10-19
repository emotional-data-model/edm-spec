"""Anchor-2 extraction (experiment-plan-anchor.md, Anchor-2 section): three arms (A wider vocabulary; B + content cues; C + length-matched
EmotionML excerpt), the same 1,000-comment GoEmotions sample as anchor-1 in the same seeded batches of 20, three repeats, the three
extractors pinned as in anchor-1, `emotion.primary` only. One record per call -> raw/<arm>/<model>.jsonl; spend -> spend_anchor2.json
(shared across arms; HARD CAP USD 11 on the whole run: the runner stops checkpointed at the cap). A re-run skips completed (repeat,
batch) jobs and re-requests a transport failure once (run 3 R3-D3). No judge.

Usage (repo root; OPENROUTER_API_KEY from .env):
  python -P experiments/2026-10-19-anchor2/scripts/run_anchor2.py --arm A --pilot [--dry-run]   # one batch per model (repeat 1, batch 0); projection
  python -P experiments/2026-10-19-anchor2/scripts/run_anchor2.py --arm A [--models SON,GEM,OSS] [--repeats 3] [--concurrency 3] [--dry-run]
"""
import argparse, asyncio, json, os, sys, time, random, re
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP); ROOT = os.path.dirname(EXPS)
M = json.load(open(os.path.join(EXP, 'models_anchor2.json'), encoding='utf-8'))
GATEWAY = M['gateway']; RAW = os.path.join(EXP, 'raw'); LEVERS_PATH = os.path.join(EXP, 'levers_anchor2.json'); SPEND_PATH = os.path.join(EXP, 'spend_anchor2.json')
SAMPLE = os.path.join(EXPS, '2026-10-18-anchor', 'data', 'sample.json')
USR = open(os.path.join(EXP, 'prompts', 'user.txt'), encoding='utf-8').read()


def load_env():
    p = os.path.join(ROOT, '.env')
    if os.path.exists(p):
        for l in open(p, encoding='utf-8'):
            l = l.strip()
            if l and not l.startswith('#') and '=' in l:
                k, v = l.split('=', 1); os.environ.setdefault(k.strip(), v.strip().strip('"'))


def levers():
    return json.load(open(LEVERS_PATH, encoding='utf-8')) if os.path.exists(LEVERS_PATH) else {}


def batches(ids, repeat, size, seed):
    rng = random.Random(seed + repeat); ids = sorted(ids); rng.shuffle(ids)
    return [ids[i:i + size] for i in range(0, len(ids), size)]


def arm_dir(model): return model.replace('/', '__')


def parse_json(text):
    t = text.strip()
    t = re.sub(r'^```(?:json)?\s*|\s*```$', '', t)
    try: return json.loads(t)
    except json.JSONDecodeError:
        i, j = t.find('{'), t.rfind('}')
        if i >= 0 and j > i: return json.loads(t[i:j + 1])
        raise


def cost_of(entry, usage):
    pr = entry['price']
    listed = (usage['input_tokens'] * pr['input'] + usage.get('cached_input_tokens', 0) * pr.get('cached_input', pr['input']) + usage.get('cache_write_tokens', 0) * pr.get('cache_write', pr['input'])
              + (usage['output_tokens']) * pr['output']) / 1e6
    billed = usage.get('billed_cost_usd')
    return (float(billed) if billed is not None else listed), listed


class Spend:
    def __init__(self, path):
        self.path = path
        self.data = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {'by_arm': {}, 'by_model': {}, 'total_usd': 0.0, 'calls': 0}

    def add(self, arm, model, cost, usage):
        for key, store in ((model, self.data['by_model']), (arm, self.data['by_arm'])):
            bm = store.setdefault(key, {'usd': 0.0, 'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'reasoning_tokens': 0})
            bm['usd'] += cost; bm['calls'] += 1; bm['input_tokens'] += usage.get('input_tokens', 0) + usage.get('cached_input_tokens', 0); bm['output_tokens'] += usage.get('output_tokens', 0); bm['reasoning_tokens'] += usage.get('reasoning_tokens', 0) or 0
        self.data['total_usd'] += cost; self.data['calls'] += 1
        json.dump(self.data, open(self.path, 'w', encoding='utf-8', newline='\n'), indent=1)


class ProviderOR:
    def __init__(self, entry, reasoning=None):
        from openai import AsyncOpenAI
        self.entry = entry; self.model = entry['model']; self.tag = entry['endpoint']['tag']; self.expect_provider = entry['endpoint']['provider_name']
        self.reasoning = reasoning; self.max_tokens = M['max_tokens']
        self.client = AsyncOpenAI(api_key=os.environ[GATEWAY['env_key']], base_url=GATEWAY['base_url'], timeout=600.0, max_retries=3,
                                  default_headers={'HTTP-Referer': 'https://github.com/emotional-data-model/edm-spec', 'X-Title': 'edm-spec anchor-2'})

    async def call(self, system, user):
        extra = {'provider': {'order': [self.tag], 'allow_fallbacks': False}}
        if self.reasoning: extra['reasoning'] = dict(self.reasoning)
        r = await self.client.chat.completions.create(model=self.model, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
                                                      response_format={'type': 'json_object'}, max_tokens=self.max_tokens, extra_body=extra)
        ch = r.choices[0]; text = ch.message.content or ''
        ud = r.usage.model_dump() if r.usage is not None else {}
        pd = ud.get('prompt_tokens_details') or {}; cd = ud.get('completion_tokens_details') or {}
        cached = pd.get('cached_tokens') or 0; cw = pd.get('cache_write_tokens') or 0
        usage = {'input_tokens': (ud.get('prompt_tokens') or 0) - cached - cw, 'output_tokens': ud.get('completion_tokens') or 0, 'cached_input_tokens': cached, 'cache_write_tokens': cw,
                 'reasoning_tokens': cd.get('reasoning_tokens') or 0, 'billed_cost_usd': ud.get('cost'), 'prompt_tokens_total': ud.get('prompt_tokens') or 0}
        rd = r.model_dump()
        return text, usage, ch.finish_reason, r.model, rd.get('provider'), rd.get('id')


class Checkpoint:
    def __init__(self, path):
        self.path = path; self.done = {}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            for l in open(path, encoding='utf-8'):
                if l.strip():
                    rec = json.loads(l); self.done[(rec['repeat'], rec['batch'])] = rec

    def append(self, rec):
        with open(self.path, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
        self.done[(rec['repeat'], rec['batch'])] = rec


def canon_answers(parsed, ids):
    """-> {id: {'primary': str|None}} for the ids present with an object (or bare string / null) value; missing ids absent."""
    out = {}
    if not isinstance(parsed, dict): return out
    src = parsed.get('answers') if isinstance(parsed.get('answers'), dict) and not any(i in parsed for i in ids) else parsed
    for i in ids:
        if i not in src: continue
        v = src.get(i)
        if isinstance(v, dict): p = v.get('primary'); out[i] = {'primary': (str(p).strip() if p is not None else None)}
        elif v is None or isinstance(v, str): out[i] = {'primary': (v.strip() if isinstance(v, str) else None)}
    return out


async def worker(prov, arm, system, jobs, ck, spend, sem, texts, stats, label, cap):
    for repeat, bi, ids in jobs:
        if stats.get('abort'): return
        lines = '\n'.join(f'{i}: {texts[i]}' for i in ids)
        user = USR.format(batch_id=f'r{repeat}b{bi}', lines=lines); t0 = time.time()
        rec = {'arm': arm, 'repeat': repeat, 'batch': bi, 'ids': ids, 'model': prov.model, 'endpoint_tag': prov.tag, 'reasoning_param_sent': prov.reasoning, 'ts': time.time()}
        raw = None; usage = None; err = None
        for attempt in range(1, 7):
            try:
                async with sem:
                    raw, usage, stop, served, provider, gen_id = await prov.call(system, user)
                rec.update({'served_model': served, 'provider': provider, 'gen_id': gen_id, 'stop_reason': stop}); err = None; break
            except Exception as e:
                msg = repr(e); err = msg[:300]
                if 'Error code: 402' in msg or 'Insufficient credits' in msg: stats['abort'] = True; print(f'  {label}: credit exhausted; run stops checkpointed'); err = 'credit: ' + err; break
                await asyncio.sleep(min(60, 5 * attempt))
        rec['latency_s'] = round(time.time() - t0, 2)
        if err:
            rec.update({'transport_error': err, 'usage': None, 'cost_usd': 0.0, 'raw_text': None, 'answers': None, 'parse_error': None, 'provider_mismatch': False}); ck.append(rec); stats['transport_fail'] += 1
            if 'credit' in err: return
            continue
        cost, listed = cost_of(prov.entry, usage); spend.add(arm, prov.model, cost, usage); stats['usd'] += cost; stats['calls'] += 1
        parsed = None; perr = None
        try: parsed = parse_json(raw)
        except Exception as e: perr = repr(e)[:200]; stats['parse_fail'] += 1
        ans = canon_answers(parsed, ids) if parsed is not None else {}
        rec.update({'usage': usage, 'cost_usd': round(cost, 6), 'cost_list_usd': round(listed, 6), 'raw_text': raw, 'answers': ans, 'n_answered': len(ans), 'parse_error': perr,
                    'provider_mismatch': (rec.get('provider') or '') != prov.expect_provider, 'transport_error': None})
        if rec['provider_mismatch']: stats['provider_mismatch'] += 1
        if len(ans) < len(ids): stats['missing_ids'] += len(ids) - len(ans)
        ck.append(rec)
        if stats['calls'] % 25 == 0 or stats['calls'] <= 3:
            print(f"  {arm}/{label}: {stats['calls']} calls, USD {stats['usd']:.2f} this run, cumulative USD {spend.data['total_usd']:.2f}; parse_fail={stats['parse_fail']} missing_ids={stats['missing_ids']} transport={stats['transport_fail']}", flush=True)
        if spend.data['total_usd'] >= cap and not stats.get('abort'):
            stats['abort'] = True; print(f'CAP USD {cap} reached (spend {spend.data["total_usd"]:.2f}); run stops checkpointed', flush=True); return


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True, choices=list(M['arms']))
    ap.add_argument('--pilot', action='store_true'); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--models', default=None)
    ap.add_argument('--repeats', type=int, default=None); ap.add_argument('--concurrency', type=int, default=3)
    a = ap.parse_args(); load_env(); lev = levers(); arm = a.arm
    system = open(os.path.join(EXP, M['arms'][arm]['system']), encoding='utf-8').read()
    sample = json.load(open(SAMPLE, encoding='utf-8')); texts = {c['id']: c['text'].replace('\n', ' ').replace('\r', ' ') for c in sample}
    ids = sorted(texts)
    arm_lev = (lev.get('arms') or {}).get(arm) or {}
    repeats = a.repeats or arm_lev.get('repeats') or M['repeats']
    keys = [k for k in M['extractors'] if (not a.models or k in a.models.split(',')) and k not in set(arm_lev.get('dropped_arms') or [])]
    plan = {}
    for k in keys:
        if a.pilot: plan[k] = [(1, 0, batches(ids, 1, M['batch_size'], M['seed'])[0])]
        else: plan[k] = [(r, bi, b) for r in range(1, repeats + 1) for bi, b in enumerate(batches(ids, r, M['batch_size'], M['seed']))]
    print(f'arm {arm}; extractors {keys}; repeats {repeats}; batch {M["batch_size"]}; jobs per extractor {[len(plan[k]) for k in keys]}; cap USD {M["cap_usd"]}', flush=True)
    spend = Spend(SPEND_PATH)
    proj = {}
    for k in keys:
        e = M['extractors'][k]; ck = Checkpoint(os.path.join(RAW, arm, f'{arm_dir(e["model"])}.jsonl'))
        costs = [r['cost_usd'] for r in ck.done.values() if r.get('usage')]
        mean = (sum(costs) / len(costs)) if costs else None
        todo = [j for j in plan[k] if (j[0], j[1]) not in ck.done or ck.done[(j[0], j[1])].get('transport_error')]
        proj[k] = {'done': len(costs), 'mean_usd': mean, 'todo': len(todo), 'projected_usd': (mean * len(todo)) if mean is not None else None}
    total_proj = spend.data['total_usd'] + sum(p['projected_usd'] or 0 for p in proj.values())
    print('projection:', json.dumps({'spent': round(spend.data['total_usd'], 4), 'per_extractor': proj, 'projected_total_usd_after_this_arm': round(total_proj, 2)}), flush=True)
    if a.dry_run: print('dry run: no call'); return 0
    if not a.pilot and all(p['mean_usd'] is not None for p in proj.values()) and total_proj > M['cap_usd']:
        print(f'projected total USD {total_proj:.2f} exceeds the cap USD {M["cap_usd"]}: apply a lever (levers_anchor2.json arms.{arm}: repeats 3 -> 2, then dropped_arms GEM) before running'); return 2
    if spend.data['total_usd'] >= M['cap_usd']: print('cap already reached; no call'); return 2
    stats = {'calls': 0, 'usd': 0.0, 'parse_fail': 0, 'transport_fail': 0, 'missing_ids': 0, 'provider_mismatch': 0}
    sem = asyncio.Semaphore(a.concurrency); tasks = []
    for k in keys:
        e = M['extractors'][k]; prov = ProviderOR(e, M['reasoning'].get(e['model']))
        ck = Checkpoint(os.path.join(RAW, arm, f'{arm_dir(e["model"])}.jsonl'))
        todo = [j for j in plan[k] if (j[0], j[1]) not in ck.done or ck.done[(j[0], j[1])].get('transport_error')]
        for j in todo: ck.done.pop((j[0], j[1]), None)
        print(f'{k} {e["model"]} @ {e["endpoint"]["tag"]}: {len(plan[k])} planned, {len(todo)} to do' + (f' [reasoning {prov.reasoning}]' if prov.reasoning else ''), flush=True)
        lanes = max(1, min(a.concurrency, len(todo)))
        for i in range(lanes): tasks.append(worker(prov, arm, system, todo[i::lanes], ck, spend, sem, texts, stats, k, M['cap_usd']))
    t0 = time.time(); await asyncio.gather(*tasks)
    print(f"done in {time.time() - t0:.0f}s: {stats['calls']} calls, USD {stats['usd']:.2f} this run; cumulative USD {spend.data['total_usd']:.2f}; parse_fail={stats['parse_fail']} missing_ids={stats['missing_ids']} transport={stats['transport_fail']} provider_mismatch={stats['provider_mismatch']}", flush=True)
    return 1 if stats.get('abort') else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
