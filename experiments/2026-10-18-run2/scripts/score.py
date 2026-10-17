"""Run-2 scoring (experiment-plan-run2.md sections 5, 7, 8): per slot x prompt arm, pooled and per corpus arm —
repeatability per extractor (judge-equivalence pair rate over the five repeats, null included), cross-model agreement over
the three voting extractors (frozen rule) and over Sonnet + GPT only (two-voter sensitivity, reported beside the frozen
verdict), cross-arm equivalence per extractor, reported-arm agreement with the voting majority, null rates, flags,
outcomes under the three-voter rule, control gate on `summary`. Writes scoring/field_table.{json,md}.

Usage: python -P experiments/2026-10-18-run2/scripts/score.py
"""
import json, os, sys
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP)
sys.path.insert(0, os.path.join(EXPS, '2026-10-17', 'scripts')); sys.path.insert(0, HERE)
from stats import pairwise_same_rate, modal  # noqa: E402
from judge import load_outputs, EXTRACTORS, ARMS, CORPUS_ARMS, SLOTS, RAW  # noqa: E402

SCORING = os.path.join(EXP, 'scoring')
VOTERS = ['claude-sonnet-5-5', 'gpt-6.1-sol', 'kimi-k2.6']; TWO = ['claude-sonnet-5-5', 'gpt-6.1-sol']; REPORTED = ['claude-haiku-5-5', 'gpt-5.4-mini']
LO_R, LO_X = 0.80, 0.60  # frozen free-text thresholds (T / L / S shapes)
SHAPE = {'subject': 'T', 'trigger': 'T', 'harm': 'T', 'drive': 'T', 'integration': 'T', 'retrieval_cues': 'L (Arm B) / T (Arm A echo)', 'summary': 'S'}


def load_judge():
    groups = {}
    d = os.path.join(RAW, 'judge')
    if not os.path.isdir(d): return groups
    for f in sorted(os.listdir(d)):
        if not f.endswith('.jsonl'): continue
        for line in open(os.path.join(d, f), encoding='utf-8'):
            if not line.strip(): continue
            r = json.loads(line)
            if r.get('groups'):
                for unit, g in r['groups'].items(): groups[(r['text_id'], unit)] = g
    return groups


def labels_of(outputs, judge, m, arm, tid, slot, nonnull=False):
    g = judge.get((tid, slot))
    if g is None: return None
    out = [g.get(f'{m}#{arm}#{rep}') for rep in sorted(outputs[m][arm].get(tid, {})) if outputs[m][arm][tid][rep] is not None]
    out = [l for l in out if l is not None]
    if nonnull: out = [l for l in out if l != 'null']
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def score(outputs, judge, texts, slot, arm):
    res = {'slot': slot, 'arm': arm, 'repeat': {}, 'null_rate': {}, 'modal': {}}
    modal_of = {m: {} for m in EXTRACTORS}; modal_nn = {m: {} for m in EXTRACTORS}
    for m in EXTRACTORS:
        rates, nn_rates, nulls, tot = [], [], 0, 0
        for tid in texts:
            labels = labels_of(outputs, judge, m, arm, tid, slot)
            if not labels: continue
            r = pairwise_same_rate(labels)
            if r is not None: rates.append(r)
            nn = [l for l in labels if l != 'null']; r2 = pairwise_same_rate(nn)
            if r2 is not None: nn_rates.append(r2)
            nulls += sum(1 for l in labels if l == 'null'); tot += len(labels)
            modal_of[m][tid] = modal(labels)
            if nn: modal_nn[m][tid] = modal(nn)
        res['repeat'][m] = {'rate': mean(rates), 'texts': len(rates), 'rate_nonnull': mean(nn_rates)}
        res['null_rate'][m] = nulls / tot if tot else None
    res['null_rate']['all'] = mean([res['null_rate'][m] for m in EXTRACTORS])
    res['null_rate']['voters'] = mean([res['null_rate'][m] for m in VOTERS])

    def cross(models, nn=False):
        src = modal_nn if nn else modal_of; xr = []
        for tid in texts:
            reps = [src[m][tid] for m in models if tid in src[m]]
            r = pairwise_same_rate(reps)
            if r is not None and len(reps) == len(models): xr.append(r)
        return {'rate': mean(xr), 'texts': len(xr)}
    res['cross3'] = cross(VOTERS); res['cross3_nonnull'] = cross(VOTERS, True)
    res['cross2'] = cross(TWO); res['cross2_nonnull'] = cross(TWO, True)
    res['cross_all5'] = cross(EXTRACTORS)
    # reported arms: agreement with the voting majority class (the class ≥ 2 of 3 voters' modal answers share)
    res['reported'] = {}
    for m in REPORTED:
        agree, n = 0, 0
        for tid in texts:
            vm = [modal_of[v][tid] for v in VOTERS if tid in modal_of[v]]
            if len(vm) < 3 or tid not in modal_of[m]: continue
            c = Counter(vm).most_common(1)[0]
            if c[1] < 2: continue
            n += 1; agree += modal_of[m][tid] == c[0]
        res['reported'][m] = {'agree_with_majority': agree / n if n else None, 'texts_with_majority': n}
    # voters: disagreement with the three-voter majority class (wrong-rate proxy, RESULTS.md section 5)
    res['_voter_disagree'] = {}
    for m in VOTERS:
        dis, n = 0, 0
        for tid in texts:
            vm = [modal_of[v][tid] for v in VOTERS if tid in modal_of[v]]
            if len(vm) < 3: continue
            c = Counter(vm).most_common(1)[0]
            if c[1] < 2: continue
            n += 1; dis += modal_of[m][tid] != c[0]
        res['_voter_disagree'][m] = dis / n if n else None
    # decisions
    stat_r = {m: res['repeat'][m]['rate'] for m in EXTRACTORS}; x3 = res['cross3']['rate']; x2 = res['cross2']['rate']
    fails = [m for m in VOTERS if stat_r[m] is not None and stat_r[m] < LO_R]; passes = [m for m in VOTERS if stat_r[m] is not None and stat_r[m] >= LO_R]
    pending = [m for m in VOTERS if stat_r[m] is None]
    if pending or x3 is None: out3 = 'pending'
    elif len(fails) >= 2: out3 = 'cut'
    elif len(fails) == 1: out3 = 'borderline-cut'
    elif x3 >= LO_X: out3 = 'pass'
    else: out3 = 'interpretive'
    f2 = [m for m in TWO if stat_r[m] is not None and stat_r[m] < LO_R]
    if any(stat_r[m] is None for m in TWO) or x2 is None: out2 = 'pending'
    elif f2: out2 = 'cut'
    elif x2 >= LO_X: out2 = 'pass'
    else: out2 = 'interpretive'
    border = any(stat_r[m] is not None and abs(stat_r[m] - LO_R) < 0.05 for m in VOTERS) or (x3 is not None and abs(x3 - LO_X) < 0.05)
    res.update({'stat_repeat': stat_r, 'voters_fail_repeat': fails, 'voters_pass_repeat': passes, 'outcome3': out3, 'outcome2': out2, 'borderline': border,
                'sparse': res['null_rate']['voters'] is not None and res['null_rate']['voters'] >= 0.90})
    res['modal'] = modal_of
    return res


def cross_arm(resA, resB, texts):
    out = {}
    for m in EXTRACTORS:
        same = n = 0; same_nn = n_nn = 0
        for tid in texts:
            a, b = resA['modal'][m].get(tid), resB['modal'][m].get(tid)
            if a is None or b is None: continue
            n += 1; same += a == b
            if a != 'null' and b != 'null': n_nn += 1; same_nn += a == b
        out[m] = {'rate': same / n if n else None, 'texts': n, 'rate_nonnull': same_nn / n_nn if n_nn else None, 'texts_nonnull': n_nn}
    out['voters_all_ge_0.60'] = all(out[m]['rate'] is not None and out[m]['rate'] >= 0.60 for m in VOTERS)
    return out


def fmt(x): return '—' if x is None else f'{x:.2f}'


def main():
    outputs, counts, arm_of = load_outputs(); judge = load_judge()
    os.makedirs(SCORING, exist_ok=True)
    by_arm = defaultdict(list)
    for tid, c in arm_of.items(): by_arm[c].append(tid)
    for c in by_arm: by_arm[c].sort()
    scopes = [('pooled', sorted(arm_of))] + [(c, by_arm[c]) for c in CORPUS_ARMS if by_arm[c]]
    table = {}
    for scope, texts in scopes:
        table[scope] = {}
        for slot in SLOTS:
            rA = score(outputs, judge, texts, slot, 'A'); rB = score(outputs, judge, texts, slot, 'B')
            xa = cross_arm(rA, rB, texts)
            for r in (rA, rB): r.pop('modal')
            nd = None if rA['null_rate']['all'] is None or rB['null_rate']['all'] is None else abs(rA['null_rate']['all'] - rB['null_rate']['all'])
            table[scope][slot] = {'A': rA, 'B': rB, 'cross_arm': xa, 'null_rate_arm_diff': nd, 'null_diff_flag': nd is not None and nd >= 0.20}
        s = table[scope]['summary']
        gate = None if s['A']['cross3']['rate'] is None or s['B']['cross3']['rate'] is None else abs(s['A']['cross3']['rate'] - s['B']['cross3']['rate'])
        table[scope]['_control_gate'] = {'summary_cross3_A': s['A']['cross3']['rate'], 'summary_cross3_B': s['B']['cross3']['rate'], 'abs_diff': gate, 'prompt_wide_drift': gate is not None and gate >= 0.10}
    json.dump({'counts': {m: dict(c) for m, c in counts.items()}, 'texts_per_arm': {c: len(v) for c, v in by_arm.items()}, 'judged_units': len(judge), 'thresholds': {'repeat': LO_R, 'cross': LO_X},
               'voters': VOTERS, 'two_voter_sensitivity': TWO, 'reported': REPORTED, 'table': table},
              open(os.path.join(SCORING, 'field_table.json'), 'w', encoding='utf-8'), indent=1, default=str)
    short = {'claude-sonnet-5-5': 'sonnet', 'gpt-6.1-sol': 'gpt', 'kimi-k2.6': 'kimi', 'claude-haiku-5-5': 'haiku', 'gpt-5.4-mini': 'mini'}
    L = ['# Run-2 per-slot scoring (generated by scripts/score.py)\n', f"Outputs: {json.dumps({m: dict(c) for m, c in counts.items()})}; judged (text, slot) units: {len(judge)}\n"]
    for scope in table:
        L.append(f'\n## {scope}\n')
        L.append('| Slot | Arm | ' + ' | '.join(f'rep {short[m]}' for m in EXTRACTORS) + ' | cross3 | cross3 nn | cross2 | null (voters) | outcome (3-voter) | 2-voter | flags |')
        L.append('|---|---|' + '---|' * len(EXTRACTORS) + '---|---|---|---|---|---|---|')
        for slot in SLOTS:
            for arm in ARMS:
                r = table[scope][slot][arm]
                flags = ', '.join(x for x, y in (('borderline', r['borderline']), ('sparse', r['sparse'])) if y)
                L.append(f"| {slot} | {arm} | " + ' | '.join(fmt(r['stat_repeat'][m]) for m in EXTRACTORS) + f" | {fmt(r['cross3']['rate'])} | {fmt(r['cross3_nonnull']['rate'])} | {fmt(r['cross2']['rate'])} | {fmt(r['null_rate']['voters'])} | **{r['outcome3']}** | {r['outcome2']} | {flags} |")
        g = table[scope]['_control_gate']
        L.append(f"\nControl gate (`summary` cross3 A {fmt(g['summary_cross3_A'])} vs B {fmt(g['summary_cross3_B'])}, diff {fmt(g['abs_diff'])}): {'PROMPT-WIDE DRIFT' if g['prompt_wide_drift'] else 'no drift'}")
        L.append('\nCross-arm equivalence (modal A == modal B, per extractor): ' + '; '.join(f"{slot}: " + ', '.join(f"{short[m]} {fmt(table[scope][slot]['cross_arm'][m]['rate'])}" for m in EXTRACTORS) for slot in SLOTS))
    open(os.path.join(SCORING, 'field_table.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('scored', {s: {slot: (table[s][slot]['A']['outcome3'], table[s][slot]['B']['outcome3']) for slot in SLOTS} for s in table})


if __name__ == '__main__':
    main()
