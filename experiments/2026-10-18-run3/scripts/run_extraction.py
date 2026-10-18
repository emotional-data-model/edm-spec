"""Run-3 extraction runner (experiment-plan-run3.md sections 2-4, 9): 150 texts x 5 repeats x 8 arms (six OpenRouter arms,
Haiku 5.5 reference, Sonnet 5.5 re-run; every arm through OpenRouter, see plan section 3), one shared 19-field system
prompt, checkpointed to raw/<arm>/<corpus_arm>.jsonl; (text_id, repeat) already present are never re-requested.

Gateway rules (plan section 3): provider = {order: [pinned endpoint tag], allow_fallbacks: false} on every call; the
response's `provider` is recorded and a record served by any other provider is a failed repeat (canon = None), never
re-sampled. Spend = the gateway's billed cost (usage.cost) with the pinned-price figure beside it -> spend.json.
Projection before the run and every 1,000 calls against the stop in force (models.json budget_usd, or --stop after the
pilot gate's lever 2); judge reserve 9.

Usage (repo root; keys from .env):
  python -P experiments/2026-10-18-run3/scripts/run_extraction.py --pilot                        # 3 texts x 8 arms x 1 repeat -> raw/pilot/
  python -P experiments/2026-10-18-run3/scripts/run_extraction.py --dry-run                      # plan, prompt check, corpus check; no call
  python -P experiments/2026-10-18-run3/scripts/run_extraction.py [--stop 60] [--reasoning-low <model,...>] [--models <id,...>]
"""
import argparse, asyncio, json, os, sys, time, hashlib, random, importlib.util
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP); ROOT = os.path.dirname(EXPS)
RUN1 = os.path.join(EXPS, '2026-10-17'); RUN2 = os.path.join(EXPS, '2026-10-18-run2')


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod); return mod


_r1 = _load('run1_extraction', os.path.join(RUN1, 'scripts', 'run_extraction.py'))   # loads .env; Spend, Checkpoint, price_of, parse_json
_r2 = _load('run2_extraction', os.path.join(RUN2, 'scripts', 'run_extraction.py'))   # parse_json2 (R2-D1: last complete object)
Spend, price_of, parse_json2 = _r1.Spend, _r1.price_of, _r2.parse_json2
_bp = _load('run3_build_prompts', os.path.join(HERE, 'build_prompts.py'))

MODELS = json.load(open(os.path.join(EXP, 'models.json'), encoding='utf-8'))
RESERVE = {'judge': 9.0}
PROMPTS = {n: open(os.path.join(EXP, 'prompts', f'{n}.txt'), encoding='utf-8').read() for n in ('extraction_system', 'extraction_user')}
SYSTEM = PROMPTS['extraction_system']
RAW = os.path.join(EXP, 'raw')
FIELDS = list(_bp.ORDERED)  # the 19 dotted paths in prompt order
CORPUS_ARMS = ('synthetic', 'conversational', 'pepys')
GATEWAY = MODELS['gateway']
LEVERS_PATH = os.path.join(EXP, 'levers.json')
LEVERS = json.load(open(LEVERS_PATH, encoding='utf-8')) if os.path.exists(LEVERS_PATH) else {}


def apply_levers(entry):
    """pilot-gate levers and logged deviations (levers.json): endpoint override (R3-D1), reasoning effort low (lever 1),
    thinking disabled on the Claude arms (R3-D2). Returns (entry, reasoning param or None)."""
    e = dict(entry)
    ov = (LEVERS.get('endpoint_overrides') or {}).get(e['model'])
    if ov:
        e['endpoint'] = {k: ov[k] for k in ('tag', 'provider_name', 'quantization', 'max_completion_tokens')}; e['price'] = ov['price']; e['endpoint_override'] = True
    if e['model'] in (LEVERS.get('thinking_disabled') or []): return e, {'enabled': False}
    cap = (LEVERS.get('reasoning_max_tokens') or {}).get(e['model'])
    if cap: return e, {'max_tokens': int(cap)}  # lever 1, token-cap form (supersedes effort low for that arm)
    if e['model'] in (LEVERS.get('reasoning_low') or []): return e, {'effort': 'low'}
    return e, None


def arm_dir(model_id): return model_id.replace('/', '__')


def check_prompts():
    """the committed prompt files must equal what build_prompts.py generates from the draft fragments now (plan section 4)."""
    out = _bp.build()
    for n, t in out.items():
        cur = open(os.path.join(EXP, 'prompts', n), encoding='utf-8').read()
        if cur != t: raise SystemExit(f'prompt drift: prompts/{n} differs from the draft-schema generation; run aborted')


def load_texts():
    """run-1 resolved texts (never committed), verified against the run-3 manifest sha256 per text; mismatch aborts."""
    man = {}
    for l in open(os.path.join(EXP, 'corpus', 'corpus_manifest.jsonl'), encoding='utf-8'):
        if l.strip(): r = json.loads(l); man[r['id']] = r
    rows = {}
    for l in open(os.path.join(RUN1, 'corpus', '.resolved_texts.jsonl'), encoding='utf-8'):
        r = json.loads(l); rows[r['id']] = r
    if set(rows) != set(man): raise SystemExit('corpus id set differs from the run-3 manifest')
    for tid, r in rows.items():
        if hashlib.sha256(r['text'].encode('utf-8')).hexdigest() != man[tid]['sha256']: raise SystemExit(f'sha256 mismatch for {tid}; run aborted')
        r['arm'] = man[tid]['arm']
    return rows


def canon(parsed):
    """-> (dict keyed by the 19 dotted paths, list of missing keys, field_confidence). Keys matched case-insensitively; a
    nested-domain form ({"narrative": {"harm": ..}}) is flattened. Shape coercion (plan section 11.3): salience.function
    -> list; scope / tether / intensity -> dict when a bare value is given (kept under the lead member)."""
    if not isinstance(parsed, dict): return None, list(FIELDS), None
    low = {}
    for k, v in parsed.items():
        kk = str(k).strip().lower()
        low.setdefault(kk, v)
        if isinstance(v, dict) and kk in ('narrative', 'emotion', 'context', 'salience', 'motivation'):
            for k2, v2 in v.items():
                k2 = str(k2).strip().lower()
                low.setdefault(f'{kk}.{k2}', v2)
                if kk == 'emotion' and k2 == 'appraisal' and isinstance(v2, dict):
                    for k3, v3 in v2.items(): low.setdefault(f'emotion.appraisal.{str(k3).strip().lower()}', v3)
    out = {}; missing = []
    for f in FIELDS:
        if f in low: out[f] = low[f]
        else: out[f] = None; missing.append(f)
    v = out['salience.function']
    if v is None: out['salience.function'] = []
    elif isinstance(v, str): out['salience.function'] = [v] if v.strip() else []
    elif not isinstance(v, list): out['salience.function'] = [str(v)]
    for f, lead in (('context.scope', 'text'), ('salience.tether', 'type'), ('emotion.intensity', 'value')):
        v = out[f]
        if v is not None and not isinstance(v, dict): out[f] = {lead: v}
    fc = low.get('field_confidence') if isinstance(low.get('field_confidence'), dict) else None
    return out, missing, fc


class ProviderOR:
    """every arm through OpenRouter: OpenAI-compatible chat completions, endpoint pinned, billed cost read back."""
    def __init__(self, entry, reasoning=None):
        from openai import AsyncOpenAI
        self.entry = entry; self.model = entry['model']; self.kind = 'openrouter'
        self.tag = entry['endpoint']['tag']; self.expect_provider = entry['endpoint']['provider_name']
        self.max_tokens = entry.get('max_tokens', GATEWAY.get('max_tokens', 12000))
        self.reasoning = reasoning  # None | {'effort': 'low'} | {'enabled': False}
        self.client = AsyncOpenAI(api_key=os.environ[GATEWAY['env_key']], base_url=GATEWAY['base_url'], timeout=600.0, max_retries=3,
                                  default_headers={'HTTP-Referer': 'https://github.com/emotional-data-model/edm-spec', 'X-Title': 'edm-spec run 3'})

    def _system(self, system):
        if self.tag.startswith('anthropic'):  # Anthropic prompt cache through the gateway (plan section 3)
            return {'role': 'system', 'content': [{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral'}}]}
        return {'role': 'system', 'content': system}

    async def call(self, system, user):
        extra = {'provider': {'order': [self.tag], 'allow_fallbacks': False}}
        if self.reasoning: extra['reasoning'] = dict(self.reasoning)
        r = await self.client.chat.completions.create(model=self.model, messages=[self._system(system), {'role': 'user', 'content': user}],
                                                      response_format={'type': 'json_object'}, max_tokens=self.max_tokens, extra_body=extra)
        ch = r.choices[0]; text = ch.message.content or ''
        ud = r.usage.model_dump() if r.usage is not None else {}
        pd = ud.get('prompt_tokens_details') or {}; cd = ud.get('completion_tokens_details') or {}
        cached = pd.get('cached_tokens') or 0; cw = pd.get('cache_write_tokens') or 0
        usage = {'input_tokens': (ud.get('prompt_tokens') or 0) - cached - cw, 'output_tokens': ud.get('completion_tokens') or 0, 'cached_input_tokens': cached,
                 'cache_write_tokens': cw, 'reasoning_tokens': cd.get('reasoning_tokens') or 0, 'billed_cost_usd': ud.get('cost'),
                 'upstream_cost_usd': (ud.get('cost_details') or {}).get('upstream_inference_cost')}
        rd = r.model_dump()
        return text, usage, ch.finish_reason, r.model, rd.get('provider'), rd.get('id')


class Checkpoint3:
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


def cost_of(entry, usage):
    listed = price_of(entry, usage)
    billed = usage.get('billed_cost_usd')
    return (float(billed) if billed is not None else listed), listed


async def worker(prov, jobs, ck, spend, sem, texts, stats, label, stop_box):
    for text_id, repeat in jobs:
        if (text_id, repeat) in ck.done: continue
        user = PROMPTS['extraction_user'].format(text_id=text_id, text=texts[text_id]['text'])
        req_sha = hashlib.sha256((prov.model + '\n' + prov.tag + '\n' + SYSTEM + '\n' + user).encode('utf-8')).hexdigest()
        attempt, delay = 0, 5; t0 = time.time()
        base = {'text_id': text_id, 'repeat': repeat, 'model': prov.model, 'endpoint_tag': prov.tag, 'reasoning_param_sent': prov.reasoning, 'request_sha256': req_sha}
        while True:
            attempt += 1; t0 = time.time()
            try:
                async with sem:
                    raw, usage, stop, served, provider, gen_id = await prov.call(SYSTEM, user)
                break
            except Exception as e:
                msg = repr(e)[:1500]
                if attempt >= 6:
                    ck.append({**base, 'ts': time.time(), 'latency_s': round(time.time() - t0, 2), 'served_model': None, 'provider': None, 'gen_id': None, 'usage': None, 'cost_usd': 0.0, 'cost_list_usd': 0.0,
                               'raw_text': None, 'parsed': None, 'canon': None, 'missing_keys': None, 'field_confidence': None, 'parse_error': None, 'transport_error': msg, 'provider_mismatch': None, 'stop_reason': None})
                    stats['transport_fail'] += 1; print(f'  [{label}] {text_id} r{repeat} TRANSPORT FAIL after {attempt} attempts: {msg}')
                    break
                await asyncio.sleep(delay + random.random() * 2); delay = min(delay * 2, 120)
                continue
        if (text_id, repeat) in ck.done: continue
        cost, listed = cost_of(prov.entry, usage)
        mismatch = (provider or '') != prov.expect_provider
        parsed, perr, cn, missing, fc = None, None, None, None, None
        try: parsed = parse_json2(raw); cn, missing, fc = canon(parsed)
        except Exception as e: perr = repr(e)[:200]
        if mismatch:  # served by an unpinned provider: a failed repeat, never re-sampled (plan section 3)
            cn = None; stats['provider_mismatch'] += 1; print(f'  [{label}] {text_id} r{repeat} PROVIDER MISMATCH: {provider!r} (pinned {prov.expect_provider})')
        rec = {**base, 'ts': time.time(), 'latency_s': round(time.time() - t0, 2), 'served_model': served, 'provider': provider, 'gen_id': gen_id, 'usage': usage, 'cost_usd': round(cost, 6), 'cost_list_usd': round(listed, 6),
               'raw_text': raw, 'parsed': parsed, 'canon': cn, 'missing_keys': missing, 'field_confidence': fc, 'parse_error': perr, 'transport_error': None, 'provider_mismatch': mismatch, 'stop_reason': stop}
        ck.append(rec); spend.add(prov.model, cost, usage)
        stats['calls'] += 1; stats['usd'] += cost
        if perr: stats['parse_fail'] += 1
        if missing: stats['missing_keys'] += 1
        if stats['calls'] % 50 == 0:
            print(f"  [{label}] {stats['calls']} calls, ${stats['usd']:.2f} this run, total ${spend.data['total_usd']:.2f}, parse_fail={stats['parse_fail']} missing_keys={stats['missing_keys']} mismatch={stats['provider_mismatch']}")
        if stats['calls'] % 1000 == 0:
            proj = project(spend, stats, stop_box['stop']); print(f'  projection after {stats["calls"]} calls: {json.dumps(proj)}')
            if proj['projected_total_usd'] > stop_box['stop']:
                write_status(f"projected total USD {proj['projected_total_usd']:.2f} exceeds the USD {stop_box['stop']} stop after {stats['calls']} calls", proj); stats['abort'] = True
        if stats.get('abort'): return


def project(spend, stats, stop):
    ext = spend.data['total_usd']; per_arm = {}
    for model, planned in stats['planned_by_model'].items():
        m = spend.data['by_model'].get(model)
        done = m['calls'] if m else 0; mean = (m['usd'] / m['calls']) if m and m['calls'] else stats['pilot_mean'].get(model, 0.0)
        per_arm[model] = {'done': done, 'mean_usd': round(mean, 5), 'projected_usd': round(planned * mean, 2)}
        ext += max(0, planned - done) * mean
    return {'spent_usd': round(spend.data['total_usd'], 2), 'completed_calls': spend.data['calls'], 'projected_extraction_usd': round(ext, 2), 'reserves_usd': RESERVE,
            'projected_total_usd': round(ext + sum(RESERVE.values()), 2), 'stop_usd': stop, 'per_arm': per_arm}


def write_status(reason, extra=None):
    p = os.path.join(EXP, 'STATUS.md')
    body = f"# STATUS (written by run_extraction.py at {time.strftime('%Y-%m-%d %H:%M:%S')})\n\n**Run stopped.** {reason}\n\n"
    if extra: body += '```json\n' + json.dumps(extra, indent=1) + '\n```\n'
    open(p, 'w', encoding='utf-8', newline='\n').write(body); print('STATUS.md written:', reason)


def pilot_means():
    out = {}
    pd = os.path.join(RAW, 'pilot')
    if not os.path.isdir(pd): return out
    for f in os.listdir(pd):
        if not f.endswith('.jsonl'): continue
        recs = [json.loads(l) for l in open(os.path.join(pd, f), encoding='utf-8') if l.strip()]
        # later pilot records of the same (text, repeat) supersede earlier ones (a re-pilot after lever 1)
        last = {}
        for r in recs: last[(r['text_id'], r['repeat'])] = r
        costs = [r['cost_usd'] for r in last.values() if r.get('usage')]
        if costs: out[recs[0]['model']] = sum(costs) / len(costs)
    return out


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', action='store_true'); ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--models', default=None)
    ap.add_argument('--corpus', default=','.join(CORPUS_ARMS)); ap.add_argument('--repeats', type=int, default=5); ap.add_argument('--concurrency', type=int, default=8)
    ap.add_argument('--repilot', action='store_true', help='pilot only: re-request the pilot texts for the selected models (after a lever); later records supersede earlier ones in the projection')
    a = ap.parse_args()
    check_prompts(); texts = load_texts()
    print(f'prompt check OK; corpus OK ({len(texts)} texts, sha256 verified)')
    stop = float(LEVERS.get('stop_usd', MODELS['budget_usd']))
    print('levers:', json.dumps({k: LEVERS.get(k) for k in ('stop_usd', 'reasoning_low', 'thinking_disabled')}), '| endpoint overrides:', list((LEVERS.get('endpoint_overrides') or {}).keys()))
    dropped = set(LEVERS.get('dropped_arms') or [])
    extractors = [e for e in MODELS['extractors'].values() if (not a.models or e['model'] in a.models.split(',')) and (a.pilot or e['model'] not in dropped)]
    if dropped and not a.pilot: print('dropped by the pilot gate (lever 3), not run:', sorted(dropped))
    corpus_arms = a.corpus.split(',')
    ids_by_arm = defaultdict(list)
    for tid, r in texts.items(): ids_by_arm[r['arm']].append(tid)
    for k in ids_by_arm: ids_by_arm[k].sort()
    if a.pilot:
        rng = random.Random(7); pilot_ids = [rng.choice(ids_by_arm[arm]) for arm in CORPUS_ARMS]
        plan = {e['model']: {'pilot': [(t, 1) for t in pilot_ids]} for e in extractors}
        raw_dir = os.path.join(RAW, 'pilot'); spend = Spend(os.path.join(EXP, 'spend_pilot.json')); print('pilot texts:', pilot_ids)
    else:
        plan = {e['model']: {carm: [(t, r) for t in ids_by_arm[carm] for r in range(1, a.repeats + 1)] for carm in corpus_arms} for e in extractors}
        raw_dir = RAW; spend = Spend(os.path.join(EXP, 'spend.json'))
    stats = {'calls': 0, 'usd': 0.0, 'parse_fail': 0, 'transport_fail': 0, 'missing_keys': 0, 'provider_mismatch': 0, 'pilot_mean': pilot_means(),
             'planned_by_model': {m: sum(len(j) for j in jobs.values()) for m, jobs in plan.items()}}
    stop_box = {'stop': stop}
    if not a.pilot:
        proj = project(spend, stats, stop); print('projection before run:', json.dumps(proj))
        if a.dry_run: print('dry run: no call'); return 0
        if proj['projected_total_usd'] > stop: write_status(f"projected total USD {proj['projected_total_usd']:.2f} exceeds the USD {stop} stop before the run", proj); return 2
    elif a.dry_run:
        print('dry run (pilot plan):', {m: len(j['pilot']) for m, j in plan.items()}); return 0
    tasks = []
    for e in extractors:
        e, reasoning = apply_levers(e)
        prov = ProviderOR(e, reasoning); sem = asyncio.Semaphore(a.concurrency)
        for carm, jobs in plan[e['model']].items():
            path = os.path.join(raw_dir, f"{arm_dir(e['model'])}.jsonl") if a.pilot else os.path.join(raw_dir, arm_dir(e['model']), f'{carm}.jsonl')
            ck = Checkpoint3(path)
            if a.pilot and a.repilot: todo = list(jobs); ck.done = {}  # re-request; the new records are appended and supersede the old in pilot_means()
            elif a.pilot: todo = [j for j in jobs if j not in ck.done or ck.done[j].get('transport_error')]  # a pilot transport failure is re-requested
            else: todo = [j for j in jobs if j not in ck.done]
            print(f"{e['model']} @ {e['endpoint']['tag']} / {carm}: {len(jobs)} planned, {len(todo)} to do" + (f' [reasoning {reasoning}]' if reasoning else ''))
            lanes = max(1, min(a.concurrency, len(todo)))
            for i in range(lanes): tasks.append(worker(prov, todo[i::lanes], ck, spend, sem, texts, stats, f"{arm_dir(e['model'])}/{carm}", stop_box))
    t0 = time.time()
    await asyncio.gather(*tasks)
    print(f"done in {time.time() - t0:.0f}s: {stats['calls']} calls, ${stats['usd']:.2f} this run; cumulative ${spend.data['total_usd']:.2f}; parse_fail={stats['parse_fail']} missing_keys={stats['missing_keys']} transport_fail={stats['transport_fail']} provider_mismatch={stats['provider_mismatch']}")
    if not a.pilot: print('final projection:', json.dumps(project(spend, stats, stop)))
    else:
        proj = project(spend, {**stats, 'pilot_mean': pilot_means(), 'planned_by_model': {e['model']: 750 for e in extractors}}, stop)
        print('PILOT GATE projection (750 calls per arm + judge reserve 9):', json.dumps(proj, indent=1))
    return 1 if stats.get('abort') else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
