"""Run-2 judge pass (experiment-plan-run2.md section 5): per text, four Opus 5.5 calls — three slot-pair groups
({subject, trigger}, {harm, drive}, {integration, retrieval_cues}) and {summary} — each receiving ALL non-null answers for
the slot from both prompt arms, all five extractors and all five repeats (up to 50 per slot), indexed, with arm and
extractor hidden; null / empty answers are pre-assigned to the "null" class and not sent. The judge groups answers into
equivalence classes (run-1 rules 1-4 + rule 5, referent not wording). Checkpointed to raw/judge/<group>.jsonl; re-runs
skip texts already judged. Spend -> spend_judge.json.

Usage: python -P experiments/2026-10-18-run2/scripts/judge.py [--limit N] [--concurrency 4]
"""
import argparse, asyncio, json, os, re, sys, time, importlib.util
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP)
RUN1 = os.path.join(EXPS, '2026-10-17')
sys.path.insert(0, os.path.join(RUN1, 'scripts'))  # stats, run-1 score


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod); return mod


R1 = _load('run1_extraction', os.path.join(RUN1, 'scripts', 'run_extraction.py'))  # Provider, Spend, price_of, parse_json
R2 = _load('run2_extraction', os.path.join(HERE, 'run_extraction.py'))  # MODELS, RAW, SLOTS, load_texts
Provider, Spend, price_of, parse_json = R1.Provider, R1.Spend, R1.price_of, R1.parse_json
MODELS, RAW, SLOTS, load_texts = R2.MODELS, R2.RAW, R2.SLOTS, R2.load_texts

JUDGE = MODELS['judge']
EXTRACTORS = [e['model'] for e in MODELS['extractors'].values()]
ARMS = ('A', 'B'); CORPUS_ARMS = ('synthetic', 'conversational', 'pepys')
GROUPS = {'g1_subject_trigger': ['subject', 'trigger'], 'g2_harm_drive': ['harm', 'drive'], 'g3_integration_cues': ['integration', 'retrieval_cues'], 'g4_summary': ['summary']}
assert sorted(u for g in GROUPS.values() for u in g) == sorted(SLOTS)
SYS = open(os.path.join(EXP, 'prompts', 'judge_system.txt'), encoding='utf-8').read()
USR = open(os.path.join(EXP, 'prompts', 'judge_user.txt'), encoding='utf-8').read()


def norm_answer(v):
    """free-text answer as shown to the judge; a list keeps its order (rule 5 reads the first element); null/empty -> None."""
    if v is None: return None
    if isinstance(v, list):
        items = [norm_answer(x) for x in v]; items = [i for i in items if i]
        return '; '.join(items) if items else None
    if isinstance(v, dict): v = v.get('text')
    if v is None: return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return s if s and s.lower() not in ('null', 'none', '[]') else None


def load_outputs(raw_dir=RAW):
    """-> outputs[model][arm][text_id][repeat] = canon dict (valid) | None (failed); counts; corpus arm per text."""
    outputs = {m: {a: defaultdict(dict) for a in ARMS} for m in EXTRACTORS}; counts = defaultdict(lambda: defaultdict(int)); arm_of = {}
    for m in EXTRACTORS:
        for a in ARMS:
            for carm in CORPUS_ARMS:
                p = os.path.join(raw_dir, m, a, f'{carm}.jsonl')
                if not os.path.exists(p): continue
                for line in open(p, encoding='utf-8'):
                    if not line.strip(): continue
                    r = json.loads(line); arm_of[r['text_id']] = carm
                    ok = isinstance(r.get('canon'), dict) and r.get('transport_error') is None
                    outputs[m][a][r['text_id']][r['repeat']] = r['canon'] if ok else None
                    counts[m]['calls'] += 1; counts[m]['valid' if ok else 'invalid'] += 1
                    if r.get('missing_keys'): counts[m]['missing_keys'] += 1
    return outputs, counts, arm_of


def answers_for(outputs, tid, units):
    out = {}
    for unit in units:
        null_keys, items = [], []
        for m in EXTRACTORS:
            for a in ARMS:
                for rep in sorted(outputs[m][a].get(tid, {})):
                    c = outputs[m][a][tid][rep]
                    if c is None: continue
                    key = f'{m}#{a}#{rep}'; t = norm_answer(c.get(unit))
                    if t is None: null_keys.append(key)
                    else: items.append((len(items), key, t))
        out[unit] = {'null': null_keys, 'items': items}
    return out


def build_block(ans):
    parts = []
    for unit, a in ans.items():
        if not a['items']: continue
        parts.append(f'### {unit}\n' + '\n'.join(f'{i}: {t}' for i, k, t in a['items']))
    return '\n\n'.join(parts)


def groups_from(ans, parsed):
    fields = parsed.get('fields', parsed)
    out = {}
    for unit, a in ans.items():
        g = {k: 'null' for k in a['null']}
        if a['items']:
            fj = fields.get(unit)
            if not isinstance(fj, dict) or not isinstance(fj.get('groups'), list): raise ValueError(f'missing groups for {unit}')
            seen = {}
            for gi, grp in enumerate(fj['groups']):
                for idx in grp:
                    idx = int(idx)
                    if idx in seen: raise ValueError(f'index {idx} in two groups for {unit}')
                    seen[idx] = f'g{gi}'
            if set(seen) != {i for i, k, t in a['items']}: raise ValueError(f'index set mismatch for {unit}: {len(seen)} vs {len(a["items"])}')
            for i, k, t in a['items']: g[k] = seen[i]
        out[unit] = g
    return out


async def judge_text(prov, sem, spend, tid, text, gname, units, outputs, ck_path, stats):
    ans = answers_for(outputs, tid, units); block = build_block(ans)
    rec = {'text_id': tid, 'group': gname, 'units': units, 'ts': time.time(), 'groups': None, 'error': None, 'usage': None, 'cost_usd': 0.0, 'raw_text': None, 'n_answers': sum(len(a['items']) for a in ans.values())}
    if not block:
        rec['groups'] = {u: {k: 'null' for k in a['null']} for u, a in ans.items()}; rec['error'] = 'all null; no call'
    else:
        user = USR.format(text_id=tid, text=text, answers_block=block)
        for attempt in range(1, 4):
            try:
                async with sem:
                    r = await prov.client.messages.create(model=prov.model, max_tokens=16000, output_config={'effort': 'low'},
                                                          system=[{'type': 'text', 'text': SYS, 'cache_control': {'type': 'ephemeral'}}],
                                                          messages=[{'role': 'user', 'content': user}])
                raw = ''.join(b.text for b in r.content if b.type == 'text'); u = r.usage
                usage = {'input_tokens': u.input_tokens, 'output_tokens': u.output_tokens, 'cached_input_tokens': getattr(u, 'cache_read_input_tokens', 0) or 0, 'cache_write_tokens': getattr(u, 'cache_creation_input_tokens', 0) or 0}
                cost = price_of(JUDGE, usage); spend.add(JUDGE['model'], cost, usage); stats['usd'] += cost
                rec['usage'] = usage; rec['cost_usd'] = round(cost, 6); rec['raw_text'] = raw
                rec['groups'] = groups_from(ans, parse_json(raw)); rec['error'] = None
                break
            except ValueError as e:
                rec['error'] = f'malformed (attempt {attempt}): {e}'
                if attempt == 3: stats['bad'] += 1
            except Exception as e:
                rec['error'] = f'transport (attempt {attempt}): {repr(e)[:200]}'
                await asyncio.sleep(5 * attempt)
    with open(ck_path, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    stats['calls'] += 1
    if stats['calls'] % 25 == 0: print(f"  judge {stats['calls']} records, ${stats['usd']:.2f} this run (bad={stats['bad']}); cumulative ${spend.data['total_usd']:.2f}")


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--limit', type=int, default=None); ap.add_argument('--concurrency', type=int, default=4)
    a = ap.parse_args()
    outputs, counts, arm_of = load_outputs()
    print('outputs:', {m: dict(c) for m, c in counts.items()})
    texts = {tid: r['text'] for tid, r in load_texts().items()}
    prov = Provider(JUDGE); sem = asyncio.Semaphore(a.concurrency); spend = Spend(os.path.join(EXP, 'spend_judge.json'))
    stats = {'calls': 0, 'usd': 0.0, 'bad': 0}
    jd = os.path.join(RAW, 'judge'); os.makedirs(jd, exist_ok=True)
    tasks = []
    for gname, units in GROUPS.items():
        ck_path = os.path.join(jd, f'{gname}.jsonl'); done = set()
        if os.path.exists(ck_path):
            for l in open(ck_path, encoding='utf-8'):
                if l.strip():
                    r = json.loads(l)
                    if r.get('groups'): done.add(r['text_id'])
        todo = [t for t in sorted(arm_of) if t not in done][:a.limit]
        print(f'{gname}: {len(todo)} texts to judge')
        for tid in todo: tasks.append(judge_text(prov, sem, spend, tid, texts[tid], gname, units, outputs, ck_path, stats))
    await asyncio.gather(*tasks)
    print(f"judge done: {stats['calls']} records, ${stats['usd']:.2f} this run, bad={stats['bad']}, cumulative spend ${spend.data['total_usd']:.2f}")


if __name__ == '__main__':
    asyncio.run(main())
