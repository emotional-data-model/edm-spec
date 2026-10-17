"""Task (b): does a stated self_position change interpretation? (experiment-plan.md section 6). API calls to the four
extractor models as raters (never the judge). Checkpointed to raw/rater/<model>.jsonl; re-runs resume.

Usage: python -P experiments/2026-10-17/scripts/task_b.py [--concurrency 4] [--score-only]
"""
import argparse, asyncio, json, os, sys, time, random
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from score import load_outputs, get_unit, norm_label, norm_text, num, EXTRACTORS, EXP, RAW, SCORING, UNITS  # noqa: E402
from stats import modal, median  # noqa: E402
from run_extraction import Provider, Spend, price_of, parse_json, MODELS  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(EXP)), 'docs', 'discovery', 'ontology-crosswalk-2026-10', 'scripts'))
import v09_layout as L  # noqa: E402

M1 = MODELS['extractors']['M1']['model']
TARGETS = ['narrative.arc', 'salience.trajectory', 'motivation.need', 'narrative.valence_shift']
CONTROL = 'context.place'
SYS = open(os.path.join(EXP, 'prompts', 'rater_system.txt'), encoding='utf-8').read()
USR = open(os.path.join(EXP, 'prompts', 'rater_user.txt'), encoding='utf-8').read()
REPEATS = 3

def modal_artifact(outputs, m, tid):
    """per-field modal (text) / median (numbers) over the model's valid repeats, keyed by the 47 dotted paths."""
    reps = [f for f in outputs[m].get(tid, {}).values() if f is not None]
    art = {}
    for path in L.ALL_09:
        vals = [f.get(path) for f in reps]
        if path in ('context.scope', 'salience.tether', 'salience.persistence') or path.startswith('emotion.valence') or path in ('emotion.arousal', 'emotion.intensity') or path.startswith('emotion.appraisal.'):
            if path in ('emotion.valence', 'emotion.arousal', 'emotion.intensity', 'emotion.appraisal.urgency', 'emotion.appraisal.control'):
                t = modal([norm_text((v or {}).get('text')) if isinstance(v, dict) else norm_text(v) for v in vals]); nums = [num(v) for v in vals]; nums = [x for x in nums if x is not None]
                art[path] = {'text': t, 'value': round(median(nums), 2) if nums else None}
            else:
                keys = {'context.scope': ['text', 'direction'], 'salience.tether': ['type', 'referent', 'stake'], 'salience.persistence': ['text', 'decay'], 'emotion.appraisal.attribution': None}[path] if path != 'emotion.appraisal.attribution' else None
                if keys: art[path] = {k: modal([norm_text((v or {}).get(k)) if isinstance(v, dict) else None for v in vals]) for k in keys}
                else: art[path] = modal([norm_text(v) for v in vals])
        elif isinstance(vals[0] if vals else None, list) or path in ('narrative.arc', 'emotion.secondary', 'context.people', 'salience.retrieval_cues', 'salience.themes', 'salience.function', 'salience.resilience'):
            lists = [tuple(norm_text(x) for x in v if norm_text(x)) if isinstance(v, list) else () for v in vals]
            art[path] = list(modal(lists)) if lists else []
        elif path in ('salience.linkage_strength',):
            nums = [num(v) for v in vals]; nums = [x for x in nums if x is not None]; art[path] = round(median(nums), 2) if nums else None
        elif path == 'narrative.turning_point':
            art[path] = modal([v if isinstance(v, bool) else None for v in vals])
        else:
            art[path] = modal([norm_text(v) for v in vals])
    return art

def build_items(outputs):
    syn = []
    for name in sorted(os.listdir(os.path.join(EXP, 'corpus'))):
        if name.startswith('synthetic_texts_months_') and name.endswith('.json'): syn += json.load(open(os.path.join(EXP, 'corpus', name), encoding='utf-8'))['texts']
    items = []
    for t in sorted(syn, key=lambda x: x['id']):
        if not t['self_position_stated']: continue
        art = modal_artifact(outputs, M1, t['id'])
        sp = art.get('narrative.self_position'); used_authored = sp is None
        if used_authored: sp = t['spans']['self_position']
        place = art.get('context.place')
        base = {k: v for k, v in art.items() if k not in ('narrative.self_position', CONTROL)}
        for k in TARGETS: base[k] = None
        items.append({'id': t['id'], 'self_position': sp, 'self_position_from_authored_span': used_authored, 'place': place, 'base': base})
    return items

def artifact_for(item, cond):
    a = dict(item['base'])
    if cond == 'B': a['narrative.self_position'] = item['self_position']
    if cond == 'Bc': a[CONTROL] = item['place']
    return json.dumps(a, ensure_ascii=False, indent=1)

async def rate(prov, sem, spend, ck_path, done, item, cond, rep, stats):
    key = (item['id'], cond, rep)
    if key in done: return
    user = USR.format(artifact_json=artifact_for(item, cond))
    rec = {'item': item['id'], 'cond': cond, 'repeat': rep, 'model': prov.model, 'ts': time.time(), 'parsed': None, 'error': None, 'usage': None, 'cost_usd': 0.0, 'raw_text': None}
    for attempt in range(1, 5):
        try:
            async with sem: raw, usage, stop, served = await prov.call(SYS, user)
            cost = price_of(prov.entry, usage); spend.add(prov.model, cost, usage); stats['usd'] += cost
            rec.update({'usage': usage, 'cost_usd': round(cost, 6), 'raw_text': raw})
            try: rec['parsed'] = parse_json(raw)
            except Exception as e: rec['error'] = f'parse: {e}'
            break
        except Exception as e:
            rec['error'] = f'transport (attempt {attempt}): {repr(e)[:200]}'; await asyncio.sleep(5 * attempt)
    with open(ck_path, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    stats['calls'] += 1
    if stats['calls'] % 50 == 0: print(f"  rater {stats['calls']} calls, ${stats['usd']:.2f}")

def load_ratings():
    d = os.path.join(RAW, 'rater'); out = defaultdict(dict)
    if not os.path.isdir(d): return out
    for f in os.listdir(d):
        if f.endswith('.jsonl'):
            for l in open(os.path.join(d, f), encoding='utf-8'):
                if l.strip():
                    r = json.loads(l); out[r['model']][(r['item'], r['cond'], r['repeat'])] = r
    return out

def score(items):
    ratings = load_ratings()
    def lab(parsed, field):
        if not isinstance(parsed, dict): return None
        v = parsed.get(field)
        if field == 'narrative.valence_shift': return (norm_text(v) or 'null').lower()
        return norm_label(v, field, {'narrative.arc': 'arc', 'salience.trajectory': 'trajectory', 'motivation.need': 'need'}.get(field))
    res = {'items': len(items), 'authored_span_used': sum(i['self_position_from_authored_span'] for i in items), 'per_rater': {}, 'pooled': {}}
    agg = defaultdict(lambda: Counter())
    for m in EXTRACTORS:
        R = ratings.get(m, {}); per = {}
        for field in TARGETS:
            c = Counter()
            for it in items:
                ref_labels = [lab(R[(it['id'], 'A', r)]['parsed'], field) for r in range(1, REPEATS + 1) if (it['id'], 'A', r) in R and R[(it['id'], 'A', r)]['parsed']]
                if not ref_labels: continue
                ref = modal(ref_labels)
                for cond in ('B', 'Bc'):
                    for r in range(1, REPEATS + 1):
                        rec = R.get((it['id'], cond, r))
                        if not rec or not rec['parsed']: continue
                        l = lab(rec['parsed'], field); c[f'{cond}_n'] += 1; c[f'{cond}_shift'] += (l != ref)
                        if field != 'narrative.valence_shift': agg[cond]['n'] += 1; agg[cond]['shift'] += (l != ref); agg[f'{cond}:{m}']['n'] += 1; agg[f'{cond}:{m}']['shift'] += (l != ref)
                        agg[f'{cond}:{field}']['n'] += 1; agg[f'{cond}:{field}']['shift'] += (l != ref)
            per[field] = {'shift_B': c['B_shift'] / c['B_n'] if c['B_n'] else None, 'shift_control': c['Bc_shift'] / c['Bc_n'] if c['Bc_n'] else None, 'readings_B': c['B_n'], 'readings_control': c['Bc_n']}
        res['per_rater'][m] = per
    rate = lambda k: (agg[k]['shift'] / agg[k]['n']) if agg[k]['n'] else None
    res['pooled'] = {'shift_B_three_coded_fields': rate('B'), 'shift_control_three_coded_fields': rate('Bc'), 'readings_B': agg['B']['n'], 'readings_control': agg['Bc']['n'],
                     'per_field': {f: {'shift_B': rate(f'B:{f}'), 'shift_control': rate(f'Bc:{f}')} for f in TARGETS},
                     'per_rater': {m: {'shift_B': rate(f'B:{m}'), 'shift_control': rate(f'Bc:{m}')} for m in EXTRACTORS}}
    b, c = res['pooled']['shift_B_three_coded_fields'], res['pooled']['shift_control_three_coded_fields']
    res['pass'] = (b is not None and c is not None and b >= 0.20 and c < 0.10)
    return res

async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--concurrency', type=int, default=4); ap.add_argument('--score-only', action='store_true')
    a = ap.parse_args()
    outputs, counts, arm_of = load_outputs()
    items = build_items(outputs)
    os.makedirs(SCORING, exist_ok=True)
    json.dump(items, open(os.path.join(SCORING, 'task_b_items.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f"{len(items)} items; authored span used for {sum(i['self_position_from_authored_span'] for i in items)}")
    if not a.score_only:
        rd = os.path.join(RAW, 'rater'); os.makedirs(rd, exist_ok=True)
        spend = Spend(os.path.join(EXP, 'spend_rater.json')); stats = {'calls': 0, 'usd': 0.0}
        tasks = []
        existing = load_ratings()
        for e in MODELS['extractors'].values():
            prov = Provider(e); sem = asyncio.Semaphore(a.concurrency if e['provider'] != 'kimi' else 2)
            ck_path = os.path.join(rd, f"{e['model']}.jsonl"); done = set(existing.get(e['model'], {}).keys())
            jobs = [(it, cond, rep) for it in items for cond in ('A', 'B', 'Bc') for rep in range(1, REPEATS + 1)]
            random.Random(20261017).shuffle(jobs)
            print(f"{e['model']}: {len(jobs)} ratings planned, {sum(1 for it, c, r in jobs if (it['id'], c, r) not in done)} to do")
            for it, cond, rep in jobs: tasks.append(rate(prov, sem, spend, ck_path, done, it, cond, rep, stats))
        await asyncio.gather(*tasks)
        print(f"rater calls done: {stats['calls']}, ${stats['usd']:.2f}; cumulative ${spend.data['total_usd']:.2f}")
    res = score(items)
    json.dump(res, open(os.path.join(SCORING, 'task_b.json'), 'w', encoding='utf-8'), indent=1)
    f = lambda x: '—' if x is None else f'{x:.2f}'
    lines = ['# Task (b): stated self_position vs control field (generated by scripts/task_b.py)\n',
             f"Items: {res['items']} (self_position taken from the authored span for {res['authored_span_used']} where M1 returned null). Raters: the four extractors × {REPEATS} repeats; reference = rater's modal reading under A.\n",
             f"**Pooled over arc / trajectory / need:** shift with self_position = {f(res['pooled']['shift_B_three_coded_fields'])} (n={res['pooled']['readings_B']}); control-field shift = {f(res['pooled']['shift_control_three_coded_fields'])} (n={res['pooled']['readings_control']}); threshold ≥ 0.20 and < 0.10 → **{'PASS' if res['pass'] else 'FAIL'}**\n",
             '| Field | shift B | shift control |', '|---|---|---|']
    for fld, d in res['pooled']['per_field'].items(): lines.append(f"| {fld} | {f(d['shift_B'])} | {f(d['shift_control'])} |")
    lines += ['', '| Rater | shift B | shift control |', '|---|---|---|']
    for m, d in res['pooled']['per_rater'].items(): lines.append(f"| {m} | {f(d['shift_B'])} | {f(d['shift_control'])} |")
    open(os.path.join(SCORING, 'task_b.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('task_b pass:', res['pass'], json.dumps(res['pooled']['per_field']))

if __name__ == '__main__':
    asyncio.run(main())
