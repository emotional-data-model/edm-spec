"""Judge pass for free-text units (experiment-plan.md section 4.2): one Opus 5.5 call per text x field group, all non-null
answers of all extractors and repeats indexed in one call; null answers are pre-assigned to group "null" and not sent.
Checkpointed to raw/judge/<group>.jsonl (one record per text); re-runs skip texts already judged.

Usage: python -P experiments/2026-10-17/scripts/judge.py [--limit N] [--concurrency 4]
"""
import argparse, asyncio, json, os, sys, time, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from score import load_outputs, get_unit, norm_text, EXTRACTORS, FREE_TEXT_UNITS, EXP, RAW  # noqa: E402
from run_extraction import Provider, Spend, price_of, parse_json, MODELS  # noqa: E402

JUDGE = MODELS['judge']
GROUPS = {
 'g1_summary': ['narrative.summary'],
 'g2_narrative': ['narrative.subject', 'narrative.trigger', 'narrative.harm', 'narrative.drive', 'narrative.integration'],
 'g3_meaning': ['narrative.meaning', 'narrative.identity_link', 'narrative.valence_shift', 'narrative.self_position', 'emotion.meta'],
 'g4_context': ['emotion.bodily_sensation', 'context.event', 'context.place', 'context.people', 'salience.tether.referent'],
 'g5_salience': ['salience.tether.stake', 'salience.retrieval_cues', 'salience.themes', 'salience.resilience'],
}
assert sorted(u for g in GROUPS.values() for u in g) == sorted(FREE_TEXT_UNITS)
SYS = open(os.path.join(EXP, 'prompts', 'judge_system.txt'), encoding='utf-8').read()
USR = open(os.path.join(EXP, 'prompts', 'judge_user.txt'), encoding='utf-8').read()

def answers_for(outputs, tid, units):
    """-> {unit: {'null': [keys], 'items': [(idx, key, text)]}}"""
    out = {}
    for unit in units:
        null_keys, items = [], []
        for m in EXTRACTORS:
            for rep in sorted(outputs[m].get(tid, {})):
                flat = outputs[m][tid][rep]
                if flat is None: continue
                key = f'{m}#{rep}'; t = norm_text(get_unit(flat, unit))
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
    """validate judge output; -> {unit: {key: group_id}} or raise."""
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
            if set(seen) != {i for i, k, t in a['items']}: raise ValueError(f'index set mismatch for {unit}: {sorted(seen)} vs {len(a["items"])}')
            for i, k, t in a['items']: g[k] = seen[i]
        out[unit] = g
    return out

async def judge_text(prov, sem, spend, tid, text, gname, units, outputs, ck_path, stats):
    ans = answers_for(outputs, tid, units)
    block = build_block(ans)
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
            except ValueError as e:  # malformed grouping: one more try with the same input (the judge is instrumentation, not a subject)
                rec['error'] = f'malformed (attempt {attempt}): {e}'
                if attempt == 3: stats['bad'] += 1
            except Exception as e:
                rec['error'] = f'transport (attempt {attempt}): {repr(e)[:200]}'
                await asyncio.sleep(5 * attempt)
    with open(ck_path, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    stats['calls'] += 1
    if stats['calls'] % 25 == 0: print(f"  judge {stats['calls']} records, ${stats['usd']:.2f} this run (bad={stats['bad']})")

async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--limit', type=int, default=None); ap.add_argument('--concurrency', type=int, default=4)
    a = ap.parse_args()
    outputs, counts, arm_of = load_outputs()
    texts = {json.loads(l)['id']: json.loads(l)['text'] for l in open(os.path.join(EXP, 'corpus', '.resolved_texts.jsonl'), encoding='utf-8')}
    prov = Provider(JUDGE); sem = asyncio.Semaphore(a.concurrency); spend = Spend(os.path.join(EXP, 'spend_judge.json'))
    stats = {'calls': 0, 'usd': 0.0, 'bad': 0}
    jd = os.path.join(RAW, 'judge'); os.makedirs(jd, exist_ok=True)
    tasks = []
    for gname, units in GROUPS.items():
        ck_path = os.path.join(jd, f'{gname}.jsonl')
        done = set()
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
