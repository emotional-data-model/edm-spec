"""R29 probe (rulings-2026-10-18.md R29): 10 calls to the Mistral Large 4 arm with an explicit reasoning budget under a raised
completion cap, to find out whether the arm's run-3 figures are a reasoning-cap artefact. Same prompt, corpus and pinned
endpoint as the main run; texts = the three pilot texts (seed 7, as run_extraction.py --pilot) + seven further texts drawn
with the same seed, one repeat each. Records -> raw/probe_r29/<arm>.jsonl (never read by score.py); spend -> spend_probe_r29.json.
Outcome printed and written to levers.json["r29_probe"]: parsed n of 10, reasoning tokens, finish reasons, cost per call,
and the ruling's branch: >= 9 of 10 parse -> "re-run the arm under these parameters"; else "reasoning-cap artefact,
excluded from the 8". Nothing else changes until the founder acts on the branch.

Usage (repo root; OPENROUTER_API_KEY from .env):
  python -P experiments/2026-10-18-run3/scripts/probe_mistral.py --dry-run
  python -P experiments/2026-10-18-run3/scripts/probe_mistral.py [--max-tokens 32000] [--reasoning-budget 8000] [--calls 10]
"""
import argparse, asyncio, json, os, sys, time, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod); return mod


R3 = _load('run3_extraction', os.path.join(HERE, 'run_extraction.py'))
ARM = 'mistralai/mistral-large-4-0'


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--max-tokens', type=int, default=32000); ap.add_argument('--reasoning-budget', type=int, default=8000); ap.add_argument('--calls', type=int, default=10)
    a = ap.parse_args()
    R3.check_prompts(); texts = R3.load_texts()
    ids_by_arm = {}
    for tid, r in texts.items(): ids_by_arm.setdefault(r['arm'], []).append(tid)
    for k in ids_by_arm: ids_by_arm[k].sort()
    rng = random.Random(7); pilot_ids = [rng.choice(ids_by_arm[arm]) for arm in R3.CORPUS_ARMS]  # the pilot's three texts, same draw
    pool = [t for arm in R3.CORPUS_ARMS for t in ids_by_arm[arm] if t not in pilot_ids]
    probe_ids = pilot_ids + rng.sample(pool, a.calls - len(pilot_ids))
    entry = next(e for e in R3.MODELS['extractors'].values() if e['model'] == ARM)
    e, _ = R3.apply_levers(entry); e = dict(e); e['max_tokens'] = a.max_tokens
    reasoning = {'max_tokens': a.reasoning_budget}
    print(f'R29 probe: {ARM} @ {e["endpoint"]["tag"]}; max_tokens {a.max_tokens}; reasoning {reasoning}; texts {probe_ids}')
    if a.dry_run: print('dry run: no call'); return 0
    prov = R3.ProviderOR(e, reasoning)
    out_dir = os.path.join(R3.RAW, 'probe_r29'); os.makedirs(out_dir, exist_ok=True)
    ck = R3.Checkpoint3(os.path.join(out_dir, f'{R3.arm_dir(ARM)}.jsonl')); spend = R3.Spend(os.path.join(EXP, 'spend_probe_r29.json'))
    results = []
    for tid in probe_ids:
        if (tid, 1) in ck.done and ck.done[(tid, 1)].get('usage'): results.append(ck.done[(tid, 1)]); continue
        user = R3.PROMPTS['extraction_user'].format(text_id=tid, text=texts[tid]['text']); t0 = time.time()
        try:
            raw, usage, stop, served, provider, gen_id = await prov.call(R3.SYSTEM, user)
        except Exception as ex:
            msg = repr(ex)[:500]; print(f'  {tid}: TRANSPORT {msg}')
            if 'Error code: 402' in msg or 'Insufficient credits' in msg: print('credit exhausted; probe stops'); break
            continue
        cost, listed = R3.cost_of(e, usage); parsed, perr, cn, missing = None, None, None, None
        try: parsed = R3.parse_json2(raw); cn, missing, _ = R3.canon(parsed)
        except Exception as ex: perr = repr(ex)[:200]
        rec = {'text_id': tid, 'repeat': 1, 'model': ARM, 'endpoint_tag': prov.tag, 'reasoning_param_sent': reasoning, 'max_tokens': a.max_tokens, 'ts': time.time(), 'latency_s': round(time.time() - t0, 2),
               'served_model': served, 'provider': provider, 'gen_id': gen_id, 'usage': usage, 'cost_usd': round(cost, 6), 'cost_list_usd': round(listed, 6), 'raw_text': raw, 'parsed': parsed, 'canon': cn,
               'missing_keys': missing, 'parse_error': perr, 'transport_error': None, 'provider_mismatch': (provider or '') != prov.expect_provider, 'stop_reason': stop}
        ck.append(rec); spend.add(ARM, cost, usage); results.append(rec)
        print(f"  {tid}: finish {stop}, reasoning {usage.get('reasoning_tokens')}, out {usage.get('output_tokens')}, USD {cost:.4f}, parsed {'yes' if cn is not None and not perr else 'NO'}")
    n = len(results); parsed_n = sum(1 for r in results if r.get('canon') is not None and not r.get('parse_error') and not r.get('provider_mismatch'))
    branch = ('re-run the arm under these parameters (>= 9 of 10 parsed)' if n >= a.calls and parsed_n >= 9 else
              ('probe incomplete' if n < a.calls else 'reasoning-cap artefact, excluded from the 8 (< 9 of 10 parsed)'))
    summary = {'when': time.strftime('%Y-%m-%d %H:%M:%S'), 'arm': ARM, 'calls': n, 'parsed': parsed_n, 'max_tokens': a.max_tokens, 'reasoning_budget': a.reasoning_budget,
               'mean_reasoning_tokens': (sum((r['usage'] or {}).get('reasoning_tokens') or 0 for r in results) / n) if n else None, 'finish_reasons': {}, 'usd': round(spend.data['total_usd'], 4), 'branch': branch}
    for r in results: summary['finish_reasons'][str(r.get('stop_reason'))] = summary['finish_reasons'].get(str(r.get('stop_reason')), 0) + 1
    lev = json.load(open(R3.LEVERS_PATH, encoding='utf-8')); lev['r29_probe'] = summary
    json.dump(lev, open(R3.LEVERS_PATH, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
    print('R29 probe:', json.dumps(summary)); return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
