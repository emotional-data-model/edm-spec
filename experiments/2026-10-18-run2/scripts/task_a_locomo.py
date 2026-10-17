"""Task (a), conversational arm, rebuilt on LoCoMo QA evidence sessions (experiment-plan-run2.md section 6; R8).
Re-analysis of the RUN-1 checkpointed outputs (experiments/2026-10-17/raw/<model>/conversational.jsonl); no API call.
Named items per conversation = the 4 sessions most cited as evidence by the LoCoMo QA set (ties: single-session citations,
then the earlier session), fixed from the ground truth alone. Policies: S = mean(intensity.value, linkage_strength)
(medians over repeats; missing component dropped; none -> ranked last), S_intensity, S_linkage; k = 3; recency keeps the
last three sessions. Pass: mean over the two blocks of (salience - recency) >= 0.10 for >= 2 of the 3 voting extractors.

Usage: python -P experiments/2026-10-18-run2/scripts/task_a_locomo.py  -> scoring/task_a_locomo.{json,md}
"""
import json, os, sys, random
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP); RUN1 = os.path.join(EXPS, '2026-10-17')
sys.path.insert(0, os.path.join(RUN1, 'scripts'))
from score import load_outputs, get_unit, num, EXTRACTORS  # noqa: E402  (run-1 loader; run-1 outputs)
from stats import median  # noqa: E402

K = 3; NAMED_N = 4; VOTERS = ['claude-sonnet-5-5', 'gpt-6.1-sol', 'kimi-k2.6']
PLAN_NAMED = {'locomo-conv-42': ['L42-02', 'L42-10', 'L42-03', 'L42-09'], 'locomo-conv-48': ['L48-02', 'L48-04', 'L48-01', 'L48-06']}  # fixed in the frozen plan section 6
POLICIES = {'S_all': ['intensity', 'linkage'], 'S_intensity': ['intensity'], 'S_linkage': ['linkage']}


def named_from_citations(block):
    cites = Counter(); single = Counter()
    for p in block['evidence']['probes']:
        for s in p['sessions']: cites[s] += 1
        if len(p['sessions']) == 1: single[p['sessions'][0]] += 1
    order = {e: i for i, e in enumerate(block['entries'])}
    ranked = sorted(block['entries'], key=lambda e: (-cites[e], -single[e], order[e]))
    return ranked[:NAMED_N], {e: cites[e] for e in block['entries']}, {e: single[e] for e in block['entries']}


def components(outputs, m, tid):
    reps = [f for f in outputs[m].get(tid, {}).values() if f is not None]
    inten = [x for x in (num(get_unit(f, 'emotion.intensity.value')) for f in reps) if x is not None]
    link = [x for x in (num(get_unit(f, 'salience.linkage_strength')) for f in reps) if x is not None]
    return {'intensity': median(inten) if inten else None, 'linkage': median(link) if link else None}


def score_S(c, use):
    vals = [c[k] for k in use if c.get(k) is not None]
    return sum(vals) / len(vals) if vals else -1.0


def hit_rate(named, retained):
    return sum(1 for n in named if n in set(retained)) / len(named)


def random_floor(block, named, draws=2000, seed=20261018):
    rng = random.Random(seed)
    return sum(hit_rate(named, rng.sample(block['entries'], K)) for _ in range(draws)) / draws


def main():
    outputs, counts, arm_of = load_outputs(arms=('conversational',))
    blocks = [b for b in json.load(open(os.path.join(RUN1, 'corpus', 'task_a_blocks.json'), encoding='utf-8'))['blocks'] if b['block'].startswith('locomo-')]
    res = {'k': K, 'named_n': NAMED_N, 'blocks': [], 'per_policy': {}}
    per = {(m, pol): [] for m in EXTRACTORS for pol in POLICIES}; sal = {(m, pol): [] for m in EXTRACTORS for pol in POLICIES}
    for b in blocks:
        named, cites, single = named_from_citations(b)
        if named != PLAN_NAMED[b['block']]: raise SystemExit(f"named sessions for {b['block']} differ from the frozen plan: {named} vs {PLAN_NAMED[b['block']]}")
        order = {e: i for i, e in enumerate(b['entries'])}
        rec_ret = sorted(b['entries'], key=lambda e: -order[e])[:K]
        row = {'block': b['block'], 'citations': cites, 'single_session_citations': single, 'named': named, 'recency_retained': rec_ret, 'recency': hit_rate(named, rec_ret), 'random': random_floor(b, named), 'models': {}}
        for m in EXTRACTORS:
            comps = {e: components(outputs, m, e) for e in b['entries']}; row['models'][m] = {'components': comps}
            for pol, use in POLICIES.items():
                ranked = sorted(b['entries'], key=lambda e: (-score_S(comps[e], use), order[e]))[:K]
                hr = hit_rate(named, ranked); row['models'][m][pol] = {'retained': ranked, 'hit_rate': hr}
                per[(m, pol)].append(hr - row['recency']); sal[(m, pol)].append(hr)
        res['blocks'].append(row)
    for pol in POLICIES:
        d = {}
        for m in EXTRACTORS:
            d[m] = {'mean_salience_hit': sum(sal[(m, pol)]) / len(sal[(m, pol)]), 'mean_diff_vs_recency': sum(per[(m, pol)]) / len(per[(m, pol)]), 'per_block_diff': per[(m, pol)]}
        n_pass = sum(1 for m in VOTERS if d[m]['mean_diff_vs_recency'] >= 0.10)
        d['voters_meeting_10pt'] = n_pass; d['pass'] = n_pass >= 2
        res['per_policy'][pol] = d
    res['recency_mean'] = sum(r['recency'] for r in res['blocks']) / len(res['blocks']); res['random_mean'] = sum(r['random'] for r in res['blocks']) / len(res['blocks'])
    sd = os.path.join(EXP, 'scoring'); os.makedirs(sd, exist_ok=True)
    json.dump(res, open(os.path.join(sd, 'task_a_locomo.json'), 'w', encoding='utf-8'), indent=1)
    f = lambda x: '—' if x is None else f'{x:.2f}'
    L = ['# Task (a), LoCoMo evidence-session ground truth, k = 3 (generated by scripts/task_a_locomo.py; run-1 outputs, no calls)\n',
         f"Recency mean {f(res['recency_mean'])}; random floor {f(res['random_mean'])}. Pass: mean (salience − recency) ≥ 0.10 for ≥ 2 of the 3 voting extractors.\n",
         '| Policy | ' + ' | '.join(f'{m}: hit / diff' for m in EXTRACTORS) + ' | voters ≥ +0.10 | pass |', '|---|' + '---|' * len(EXTRACTORS) + '---|---|']
    for pol in POLICIES:
        d = res['per_policy'][pol]
        L.append(f'| {pol} | ' + ' | '.join(f"{f(d[m]['mean_salience_hit'])} / {f(d[m]['mean_diff_vs_recency'])}" for m in EXTRACTORS) + f" | {d['voters_meeting_10pt']} | {'**yes**' if d['pass'] else 'no'} |")
    L.append('\n| Block | named | recency keeps | recency | random | ' + ' | '.join(f'{m} S_all keeps / hit' for m in EXTRACTORS) + ' |\n|---|---|---|---|---|' + '---|' * len(EXTRACTORS))
    for r in res['blocks']:
        L.append(f"| {r['block']} | {', '.join(r['named'])} | {', '.join(r['recency_retained'])} | {f(r['recency'])} | {f(r['random'])} | " + ' | '.join(f"{', '.join(r['models'][m]['S_all']['retained'])} / {f(r['models'][m]['S_all']['hit_rate'])}" for m in EXTRACTORS) + ' |')
    open(os.path.join(sd, 'task_a_locomo.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print({pol: res['per_policy'][pol]['pass'] for pol in POLICIES}, 'recency', round(res['recency_mean'], 3), 'random', round(res['random_mean'], 3))


if __name__ == '__main__':
    main()
