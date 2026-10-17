"""Task (a): salience-weighted vs recency-weighted retention (experiment-plan.md section 5). No API calls.
Usage: python -P experiments/2026-10-17/scripts/task_a.py  -> scoring/task_a.{json,md}
"""
import json, os, sys, random
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from score import load_outputs, get_unit, norm_label, num, EXTRACTORS, EXP, SCORING, PERSISTENCE_RANK  # noqa: E402
from stats import median, modal  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(EXP)), 'docs', 'discovery', 'ontology-crosswalk-2026-10', 'scripts'))
import v09_layout as L  # noqa: E402

K = 3

def components(outputs, m, tid):
    reps = [f for f in outputs[m].get(tid, {}).values() if f is not None]
    inten = [num(get_unit(f, 'emotion.intensity.value')) for f in reps]; inten = [x for x in inten if x is not None]
    link = [num(get_unit(f, 'salience.linkage_strength')) for f in reps]; link = [x for x in link if x is not None]
    ptext = modal([norm_label(get_unit(f, 'salience.persistence.text'), 'salience.persistence.text', 'persistence') for f in reps]) if reps else None
    pdecay = modal([norm_label(get_unit(f, 'salience.persistence.decay'), 'salience.persistence.decay', None) for f in reps]) if reps else None
    code = L.PERSISTENCE_RECODE.get(ptext) or L.DECAY_RECODE.get(pdecay) or (ptext if ptext in PERSISTENCE_RANK else None)
    return {'intensity': median(inten) if inten else None, 'linkage': median(link) if link else None, 'persistence': PERSISTENCE_RANK.get(code)}

def score_S(c, use):
    vals = [c[k] for k in use if c.get(k) is not None]
    return sum(vals) / len(vals) if vals else -1.0

def hit_rate(block, retained):
    ev = block['evidence']; retained = set(retained)
    if ev['kind'] == 'benchmark_qa_evidence':
        probes = ev['probes']
        return sum(1 for p in probes if set(p['sessions']) <= retained) / len(probes) if probes else None
    named = block['named']
    return sum(1 for n in named if n in retained) / len(named) if named else None

def random_floor(block, draws=1000, seed=20261017):
    rng = random.Random(seed); ents = block['entries']
    rates = [hit_rate(block, rng.sample(ents, K)) for _ in range(draws)]
    rates = [r for r in rates if r is not None]
    return sum(rates) / len(rates) if rates else None

def main():
    outputs, counts, arm_of = load_outputs()
    blocks = json.load(open(os.path.join(EXP, 'corpus', 'task_a_blocks.json'), encoding='utf-8'))['blocks']
    POLICIES = {'S_all': ['intensity', 'linkage', 'persistence'], 'S_intensity': ['intensity'], 'S_linkage': ['linkage'], 'S_persistence': ['persistence']}
    res = {'k': K, 'per_block': [], 'per_arm': {}, 'pooled': {}}
    per = defaultdict(lambda: defaultdict(list))  # (arm, model, policy) -> rates
    for b in blocks:
        order = {e: i for i, e in enumerate(b['entries'])}
        rec_ret = sorted(b['entries'], key=lambda e: -order[e])[:K]
        row = {'block': b['block'], 'arm': b['arm'], 'recency': hit_rate(b, rec_ret), 'random': random_floor(b), 'models': {}}
        for m in EXTRACTORS:
            comps = {e: components(outputs, m, e) for e in b['entries']}
            row['models'][m] = {}
            for pol, use in POLICIES.items():
                ranked = sorted(b['entries'], key=lambda e: (-score_S(comps[e], use), order[e]))[:K]  # ties -> earlier entry
                hr = hit_rate(b, ranked)
                row['models'][m][pol] = {'retained': ranked, 'hit_rate': hr}
                if hr is not None and row['recency'] is not None:
                    per[(b['arm'], m, pol)]['diff'].append(hr - row['recency']); per[(b['arm'], m, pol)]['sal'].append(hr)
                    per[('pooled', m, pol)]['diff'].append(hr - row['recency']); per[('pooled', m, pol)]['sal'].append(hr)
            row['models'][m]['components'] = comps
        res['per_block'].append(row)
    arms = sorted({b['arm'] for b in blocks}) + ['pooled']
    for arm in arms:
        out = {}
        for pol in POLICIES:
            d = {}
            for m in EXTRACTORS:
                diffs = per[(arm, m, pol)]['diff']; sal = per[(arm, m, pol)]['sal']
                d[m] = {'mean_salience_hit': sum(sal) / len(sal) if sal else None, 'mean_diff_vs_recency': sum(diffs) / len(diffs) if diffs else None, 'blocks': len(diffs)}
            n_pass = sum(1 for m in EXTRACTORS if d[m]['mean_diff_vs_recency'] is not None and d[m]['mean_diff_vs_recency'] >= 0.10)
            d['models_meeting_10pt'] = n_pass; d['pass'] = n_pass >= 3
            out[pol] = d
        rec = [r['recency'] for r in res['per_block'] if (arm == 'pooled' or r['arm'] == arm) and r['recency'] is not None]
        rnd = [r['random'] for r in res['per_block'] if (arm == 'pooled' or r['arm'] == arm) and r['random'] is not None]
        out['recency_mean'] = sum(rec) / len(rec) if rec else None; out['random_mean'] = sum(rnd) / len(rnd) if rnd else None
        (res['per_arm'] if arm != 'pooled' else res)['pooled' if arm == 'pooled' else arm] = out
    os.makedirs(SCORING, exist_ok=True)
    json.dump(res, open(os.path.join(SCORING, 'task_a.json'), 'w', encoding='utf-8'), indent=1)
    f = lambda x: '—' if x is None else f'{x:.2f}'
    lines = ['# Task (a): salience vs recency retention, k = 3 (generated by scripts/task_a.py)\n']
    for arm in arms:
        o = res['per_arm'][arm] if arm != 'pooled' else res['pooled']
        lines.append(f"\n## {arm}  (recency mean {f(o['recency_mean'])}, random floor {f(o['random_mean'])})\n")
        lines.append('| Policy | ' + ' | '.join(f'{m}: salience hit / diff' for m in EXTRACTORS) + ' | models ≥ +0.10 | pass (≥3 of 4) |')
        lines.append('|---|' + '---|' * len(EXTRACTORS) + '---|---|')
        for pol in POLICIES:
            d = o[pol]
            lines.append(f'| {pol} | ' + ' | '.join(f"{f(d[m]['mean_salience_hit'])} / {f(d[m]['mean_diff_vs_recency'])}" for m in EXTRACTORS) + f" | {d['models_meeting_10pt']} | {'**yes**' if d['pass'] else 'no'} |")
    lines.append('\n## Per block (S_all)\n\n| Block | recency | random | ' + ' | '.join(EXTRACTORS) + ' |\n|---|---|---|' + '---|' * len(EXTRACTORS))
    for r in res['per_block']:
        lines.append(f"| {r['block']} | {f(r['recency'])} | {f(r['random'])} | " + ' | '.join(f(r['models'][m]['S_all']['hit_rate']) for m in EXTRACTORS) + ' |')
    open(os.path.join(SCORING, 'task_a.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print(json.dumps({arm: {pol: (res['per_arm'][arm] if arm != 'pooled' else res['pooled'])[pol]['pass'] for pol in POLICIES} for arm in arms}))

if __name__ == '__main__':
    main()
