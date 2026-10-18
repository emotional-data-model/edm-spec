"""Run-3 scoring (experiment-plan-run3.md sections 6-8): per arm x field (19 lead units) — repeatability (Fleiss kappa /
ICC(2,1) / judge pair rate), agreement with the voting majority (Cohen's kappa / ICC / judge class match; majority =
Sonnet 5.5 from THIS run + gpt-6.1-sol and Kimi K2.6 from run 1, run-2 Arm B representatives for harm), coverage,
null rate, non-canonical rate; the frozen section-7 decision per cell (holds / repeats only / does not hold / uncovered),
the per-field 5-of-9 verdict, bands and predictions P1-P4, the framing bound (Sonnet run 1 vs run 3, Q5), descriptive
cross-model agreement among the new arms, and per-arm raw statistics (provider, reasoning tokens, cost, truncations).
Writes scoring/field_table.{json,md}.

Usage: python -P experiments/2026-10-18-run3/scripts/score.py
"""
import json, os, sys, glob
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP)
RUN1 = os.path.join(EXPS, '2026-10-17')
sys.path.insert(0, os.path.join(RUN1, 'scripts')); sys.path.insert(0, HERE)
from stats import fleiss_kappa, icc2_1, pairwise_same_rate, modal  # noqa: E402
import judge as J  # noqa: E402
R1S = J.R1S; MODELS = J.MODELS; RAW = J.RAW
ARMS, NEW_ARMS, REF, SON = J.ARMS, J.NEW_ARMS, J.REF, J.SON
VOTERS_R1 = ['gpt-6.1-sol', 'kimi-k2.6']; SON_R1 = 'claude-sonnet-5-5'
SCORING = os.path.join(EXP, 'scoring')
THRESH = {'C': (0.70, 0.40), 'CL': (0.70, 0.40), 'B': (0.70, 0.40), 'T': (0.80, 0.60), 'S': (0.80, 0.60), 'D': (0.75, 0.50)}
UNITS = [('narrative.harm', 'T', None), ('narrative.summary', 'S', None), ('narrative.meaning', 'T', None), ('narrative.turning_point', 'B', None), ('narrative.self_position', 'T', None),
         ('emotion.primary', 'C', 'emotion'), ('emotion.valence.text', 'C', 'valence'), ('emotion.intensity.value', 'D', None), ('emotion.bodily_sensation', 'T', None), ('emotion.appraisal.attribution', 'C', 'attribution'),
         ('context.event_category', 'C', 'event_category'), ('context.relationship', 'C', 'relationship'), ('context.scope.text', 'C', 'scope'), ('salience.tether.type', 'C', 'tether'), ('salience.function', 'CL', 'function'),
         ('motivation.action_tendency', 'C', 'action_tendency'), ('motivation.need', 'C', 'need'), ('motivation.temporal_focus', 'C', 'temporal_focus'), ('motivation.coping', 'C', 'coping')]
FIELD_OF = {u: (u.rsplit('.', 1)[0] if u.endswith(('.text', '.value', '.type')) else u) for u, s, v in UNITS}
P1_SET = [e['model'] for e in MODELS['extractors'].values() if e.get('p1_open_weight_set')]
GEMINI = 'google/gemini-4-argon'
BAND_CHEAP, BAND_VOTING = 13, 17


def get_unit3(canon, unit):
    """lead-unit value from a run-3 canon dict (19 field keys; sub-members in dicts; valence a bare string)."""
    if unit in canon: return canon.get(unit)
    base, _, sub = unit.rpartition('.')
    v = canon.get(base)
    if isinstance(v, dict): return v.get(sub)
    if sub == 'text': return v
    return None


def cohen_kappa(pairs):
    """pairs: list of (a, b) labels. -> (kappa, raw agreement, n). kappa None when undefined; perfect agreement on one category -> 1.0."""
    n = len(pairs)
    if n < 2: return None, (sum(1 for a, b in pairs if a == b) / n if n else None), n
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, b in pairs); cb = Counter(b for a, b in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if abs(1 - pe) < 1e-12: return (1.0 if po == 1.0 else None), po, n
    return (po - pe) / (1 - pe), po, n


def kappa_or_one(k, info):
    return 1.0 if (k is None and info.get('P_bar') == 1.0) else k


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


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


def raw_arm_stats():
    out = {}
    for m in ARMS:
        c = Counter(); prov = Counter(); reas = []; outs = []; costs = []; lat = []
        for p in glob.glob(os.path.join(RAW, J.R3.arm_dir(m), '*.jsonl')):
            for l in open(p, encoding='utf-8'):
                if not l.strip(): continue
                r = json.loads(l); c['calls'] += 1
                if r.get('transport_error'): c['transport'] += 1; continue
                if r.get('provider_mismatch'): c['provider_mismatch'] += 1
                if r.get('parse_error'): c['parse'] += 1
                if r.get('missing_keys'): c['missing_keys'] += 1
                if r.get('stop_reason') == 'length': c['truncated'] += 1
                prov[r.get('provider')] += 1; u = r.get('usage') or {}
                reas.append(u.get('reasoning_tokens') or 0); outs.append(u.get('output_tokens') or 0); costs.append(r.get('cost_usd') or 0); lat.append(r.get('latency_s') or 0)
        out[m] = {'counts': dict(c), 'providers': dict(prov), 'mean_reasoning_tokens': mean(reas), 'mean_output_tokens': mean(outs), 'mean_cost_usd': mean(costs), 'mean_latency_s': mean(lat), 'usd': sum(costs)}
    return out


def score_unit(unit, shape, vocab, outputs, out1, judge, texts):
    lo_r, lo_x = THRESH[shape]
    res = {'unit': unit, 'field': FIELD_OF[unit], 'shape': shape, 'arms': {}, 'majority': {}, 'framing': {}, 'cross_new': None}
    canon_set = J.R3._bp.L.CANONICAL.get(vocab) if vocab else None
    if shape in ('C', 'CL', 'B'):
        # labels per source: run-3 arms; run-1 voters
        lab3 = {m: {tid: [R1S.norm_label(get_unit3(c, unit), unit, vocab) for rep in sorted(outputs[m].get(tid, {})) if (c := outputs[m][tid][rep]) is not None] for tid in texts} for m in ARMS}
        lab1 = {v: {tid: [R1S.norm_label(R1S.get_unit(f, unit), unit, vocab) for rep in sorted(out1[v].get(tid, {})) if (f := out1[v][tid][rep]) is not None] for tid in texts} for v in VOTERS_R1 + [SON_R1]}
        mod3 = {m: {tid: modal(l) for tid, l in lab3[m].items() if l} for m in ARMS}
        mod1 = {v: {tid: modal(l) for tid, l in lab1[v].items() if l} for v in lab1}
        # majority: Sonnet run 3 + gpt / kimi run 1
        maj = {}
        for tid in texts:
            votes = [d[tid] for d in (mod3[SON], mod1['gpt-6.1-sol'], mod1['kimi-k2.6']) if tid in d]
            if len(votes) < 2: continue
            c = Counter(votes).most_common(1)[0]
            if c[1] >= 2: maj[tid] = c[0]
        res['majority'] = {'texts_with_majority': len(maj), 'exclusion_rate': 1 - len(maj) / len(texts), 'null_share_of_majority': (sum(1 for v in maj.values() if v == 'null') / len(maj)) if maj else None}
        for m in ARMS:
            k, info = fleiss_kappa([lab3[m][tid] for tid in texts]); rep = kappa_or_one(k, info)
            pairs = [(mod3[m][tid], maj[tid]) for tid in texts if tid in maj and tid in mod3[m]]
            ck, po, n = cohen_kappa(pairs)
            covered = sum(1 for a, b in pairs if a != 'null'); cov = covered / len(texts)
            alll = [l for tid in texts for l in lab3[m][tid]]
            nulls = sum(1 for l in alll if l == 'null'); nn = [l for l in alll if l != 'null']
            noncan = (sum(1 for l in nn if l not in canon_set) / len(nn)) if (canon_set and nn) else None
            res['arms'][m] = {'repeat': rep, 'repeat_subjects': info.get('subjects'), 'agree': ck, 'agree_raw': po, 'agree_texts': n, 'coverage': cov, 'null_rate': (nulls / len(alll)) if alll else None,
                              'noncanonical_rate': noncan, 'n_valid_outputs': len(alll), 'modal_dist': dict(Counter(mod3[m].values()).most_common(6))}
        # framing bound: Sonnet run 1 vs run 3
        pairs = [(mod1[SON_R1][tid], mod3[SON][tid]) for tid in texts if tid in mod1[SON_R1] and tid in mod3[SON]]
        fk, fpo, fn = cohen_kappa(pairs); res['framing'] = {'kappa': fk, 'raw': fpo, 'texts': fn}
        # cross-model among the new arms (descriptive)
        rows = [[mod3[m][tid] for m in NEW_ARMS if tid in mod3[m]] for tid in texts]
        k, info = fleiss_kappa(rows); res['cross_new'] = {'kappa': kappa_or_one(k, info), 'subjects': info.get('subjects')}
        # run-1 voters' own repeatability / nulls for reference
        res['voters_run1'] = {v: {'repeat': kappa_or_one(*fleiss_kappa([lab1[v][tid] for tid in texts]))} for v in VOTERS_R1 + [SON_R1]}
    elif shape == 'D':
        num3 = {m: {tid: [x for rep in sorted(outputs[m].get(tid, {})) if (c := outputs[m][tid][rep]) is not None for x in [R1S.num(get_unit3(c, unit))]] for tid in texts} for m in ARMS}
        num1 = {v: {tid: [x for rep in sorted(out1[v].get(tid, {})) if (f := out1[v][tid][rep]) is not None for x in [R1S.num(R1S.get_unit(f, unit))]] for tid in texts} for v in VOTERS_R1 + [SON_R1]}
        def means(d): return {tid: (sum(n) / len(n)) for tid, vals in d.items() if (n := [x for x in vals if x is not None])}
        mean3 = {m: means(num3[m]) for m in ARMS}; mean1 = {v: means(num1[v]) for v in num1}
        maj = {}
        for tid in texts:
            vs = [d[tid] for d in (mean3[SON], mean1['gpt-6.1-sol'], mean1['kimi-k2.6']) if tid in d]
            if vs: maj[tid] = sum(vs) / len(vs)
        res['majority'] = {'texts_with_majority': len(maj), 'exclusion_rate': 1 - len(maj) / len(texts), 'voters_giving_numbers_mean': mean([sum(1 for d in (mean3[SON], mean1['gpt-6.1-sol'], mean1['kimi-k2.6']) if tid in d) for tid in maj])}
        for m in ARMS:
            full = [v for tid in texts if len((v := [x for x in num3[m][tid] if x is not None])) == 5]
            icc = icc2_1(full) if len(full) >= 2 else None
            both = [(mean3[m][tid], maj[tid]) for tid in texts if tid in maj and tid in mean3[m]]
            x = icc2_1([[a, b] for a, b in both]) if len(both) >= 2 else None
            alln = [x for tid in texts for x in num3[m][tid]]; n_valid = sum(len(num3[m][tid]) for tid in texts)
            res['arms'][m] = {'repeat': icc, 'repeat_texts_complete': len(full), 'agree': x, 'agree_texts': len(both), 'coverage': len(both) / len(texts), 'null_rate': (sum(1 for v in alln if v is None) / n_valid) if n_valid else None,
                              'texts_with_number': len(mean3[m]), 'n_valid_outputs': n_valid}
        both = [(mean1[SON_R1][tid], mean3[SON][tid]) for tid in texts if tid in mean1[SON_R1] and tid in mean3[SON]]
        res['framing'] = {'icc': icc2_1([[a, b] for a, b in both]) if len(both) >= 2 else None, 'texts': len(both)}
        rows = [[mean3[m][tid] for m in NEW_ARMS] for tid in texts if all(tid in mean3[m] for m in NEW_ARMS)]
        res['cross_new'] = {'icc': icc2_1(rows) if len(rows) >= 2 else None, 'texts_complete': len(rows)}
    else:  # T / S via the judge
        def labels(m, tid):
            g = judge.get((tid, unit))
            if g is None: return None
            return [l for rep in sorted(outputs[m].get(tid, {})) if outputs[m][tid][rep] is not None and (l := g.get(f'{m}#{rep}')) is not None]
        rep3 = {m: {} for m in ARMS}; rates = {m: [] for m in ARMS}; nn_rates = {m: [] for m in ARMS}; nulls = {m: [0, 0] for m in ARMS}
        for m in ARMS:
            for tid in texts:
                ls = labels(m, tid)
                if not ls: continue
                r = pairwise_same_rate(ls)
                if r is not None: rates[m].append(r)
                r2 = pairwise_same_rate([l for l in ls if l != 'null'])
                if r2 is not None: nn_rates[m].append(r2)
                rep3[m][tid] = modal(ls); nulls[m][0] += sum(1 for l in ls if l == 'null'); nulls[m][1] += len(ls)
        maj = {}; excluded_no_judge = 0
        for tid in texts:
            g = judge.get((tid, unit))
            if g is None: excluded_no_judge += 1; continue
            votes = [x for x in (rep3[SON].get(tid), g.get('rep:gpt-6.1-sol'), g.get('rep:kimi-k2.6')) if x is not None]
            if len(votes) < 2: continue
            c = Counter(votes).most_common(1)[0]
            if c[1] >= 2: maj[tid] = c[0]
        res['majority'] = {'texts_with_majority': len(maj), 'exclusion_rate': 1 - len(maj) / len(texts), 'texts_without_judge': excluded_no_judge, 'null_share_of_majority': (sum(1 for v in maj.values() if v == 'null') / len(maj)) if maj else None}
        for m in ARMS:
            inc = [tid for tid in texts if tid in maj and tid in rep3[m]]
            agree = sum(1 for tid in inc if rep3[m][tid] == maj[tid]); covered = sum(1 for tid in inc if rep3[m][tid] != 'null')
            inc_nn = [tid for tid in inc if rep3[m][tid] != 'null' and maj[tid] != 'null']
            res['arms'][m] = {'repeat': mean(rates[m]), 'repeat_nonnull': mean(nn_rates[m]), 'repeat_texts': len(rates[m]), 'agree': (agree / len(inc)) if inc else None, 'agree_texts': len(inc),
                              'agree_nonnull': (sum(1 for tid in inc_nn if rep3[m][tid] == maj[tid]) / len(inc_nn)) if inc_nn else None, 'agree_nonnull_texts': len(inc_nn),
                              'coverage': covered / len(texts), 'null_rate': (nulls[m][0] / nulls[m][1]) if nulls[m][1] else None, 'n_valid_outputs': nulls[m][1]}
        fb = []; fb_nn = []
        for tid in texts:
            g = judge.get((tid, unit))
            if g is None or tid not in rep3[SON] or g.get('rep:claude-sonnet-5-5@classing-run') is None: continue
            a, b = g['rep:claude-sonnet-5-5@classing-run'], rep3[SON][tid]; fb.append(a == b)
            if a != 'null' and b != 'null': fb_nn.append(a == b)
        res['framing'] = {'rate': mean([1.0 if x else 0.0 for x in fb]) if fb else None, 'texts': len(fb), 'rate_nonnull': mean([1.0 if x else 0.0 for x in fb_nn]) if fb_nn else None, 'texts_nonnull': len(fb_nn)}
        xr = []
        for tid in texts:
            reps = [rep3[m][tid] for m in NEW_ARMS if tid in rep3[m]]
            r = pairwise_same_rate(reps)
            if r is not None and len(reps) == len(NEW_ARMS): xr.append(r)
        res['cross_new'] = {'rate': mean(xr), 'texts': len(xr)}
        if not judge: res['notes'] = ['judge pending']
    # decisions per arm (plan section 7)
    for m, a in res['arms'].items():
        r, x, cov = a.get('repeat'), a.get('agree'), a.get('coverage') or 0
        if r is None or x is None: d = 'pending' if not judge and shape in ('T', 'S') else ('uncovered' if cov < 0.5 else 'does not hold')
        elif cov < 0.5: d = 'uncovered'
        elif r >= lo_r and x >= lo_x: d = 'holds'
        elif r >= lo_r: d = 'repeats only'
        else: d = 'does not hold'
        a['decision'] = d; a['repeat_met'] = r is not None and r >= lo_r; a['agree_met'] = x is not None and x >= lo_x
        a['borderline'] = (r is not None and abs(r - lo_r) < 0.05) or (x is not None and abs(x - lo_x) < 0.05)
        a['sparse'] = a.get('null_rate') is not None and a['null_rate'] >= 0.90
    arms_run = [m for m in NEW_ARMS if res['arms'].get(m, {}).get('n_valid_outputs')]
    n_hold_new = sum(1 for m in arms_run if res['arms'][m]['decision'] == 'holds')
    res['verdict'] = {'new_arms_run': len(arms_run), 'new_arms_hold': n_hold_new, 'new_arms_repeat_only': sum(1 for m in arms_run if res['arms'][m]['decision'] == 'repeats only'),
                      'total_hold_of': 3 + len(arms_run), 'total_hold': 3 + n_hold_new, 'holds_across_market': (3 + n_hold_new) >= 5,
                      'recommendation': None if (3 + n_hold_new) >= 5 else 're-class interpretive (R17: Essential -> Extended); founder rules'}
    return res


def main():
    outputs, counts, arm_of, providers = J.load_outputs(); judge = load_judge()
    out1, _, _ = R1S.load_outputs(models=VOTERS_R1 + [SON_R1])
    texts = sorted(arm_of); by_arm = defaultdict(list)
    for tid, c in arm_of.items(): by_arm[c].append(tid)
    os.makedirs(SCORING, exist_ok=True)
    table = {}
    for scope, ts in [('pooled', texts)] + [(c, sorted(by_arm[c])) for c in J.CORPUS_ARMS if by_arm[c]]:
        table[scope] = {u: score_unit(u, s, v, outputs, out1, judge, ts) for u, s, v in UNITS}
    P = table['pooled']
    # bands per arm
    bands = {}
    for m in ARMS:
        rep_met = sum(1 for u, s, v in UNITS if P[u]['arms'].get(m, {}).get('repeat_met')); holds = sum(1 for u, s, v in UNITS if P[u]['arms'].get(m, {}).get('decision') == 'holds')
        agree_met = sum(1 for u, s, v in UNITS if P[u]['arms'].get(m, {}).get('agree_met'))
        band = 'cheap-tier' if rep_met <= BAND_CHEAP else ('voting' if rep_met >= BAND_VOTING else 'between')
        bands[m] = {'repeat_met': rep_met, 'agree_met': agree_met, 'holds': holds, 'repeats_only': sum(1 for u, s, v in UNITS if P[u]['arms'].get(m, {}).get('decision') == 'repeats only'),
                    'uncovered': sum(1 for u, s, v in UNITS if P[u]['arms'].get(m, {}).get('decision') == 'uncovered'), 'band': band, 'in_p1_set': m in P1_SET, 'is_new_arm': m in NEW_ARMS}
    # predictions
    p1_arms = {m: (bands[m]['band'] == 'cheap-tier' and bands[m]['holds'] <= 10) for m in P1_SET if bands[m]['repeat_met'] or counts[m]['valid']}
    fail = [u for u, s, v in UNITS if not P[u]['verdict']['holds_across_market']]
    hold_counts = {FIELD_OF[u]: P[u]['verdict']['total_hold'] for u, s, v in UNITS}
    p3_first = ['motivation.action_tendency', 'context.scope', 'motivation.need']; p3_robust = ['emotion.primary', 'emotion.valence', 'emotion.appraisal.attribution', 'emotion.bodily_sensation', 'narrative.summary']
    lowest = min(hold_counts.values()) if hold_counts else None
    p3a = all(f in fail or hold_counts[f] == lowest for f in p3_first) and bool(fail)
    p3a_strict = set(f.split('.')[-1] for f in fail) >= set(f.split('.')[-1] for f in p3_first) if fail else False
    p3b = all(hold_counts[f] >= 8 for f in p3_robust)
    iu = 'emotion.intensity.value'; p4_arms = {m: (P[iu]['arms'][m]['null_rate'] or 0) >= 0.5 for m in NEW_ARMS if P[iu]['arms'].get(m)}
    predictions = {
        'P1': {'held': bool(p1_arms) and all(p1_arms.values()), 'per_arm': p1_arms, 'rule': 'each open-weight arm (weights public at freeze) in the cheap-tier band (repeat met on <= 13 of 19) and holds <= 10 of 19'},
        'P2': {'held': bands[GEMINI]['repeat_met'] >= 17 and bands[GEMINI]['holds'] >= 15, 'gemini': bands[GEMINI], 'rule': 'Gemini repeat met on >= 17 and holds >= 15'},
        'P3': {'held': p3a_strict and p3b, 'first_to_fail_in_failing_set': p3a_strict, 'first_to_fail_lowest_counts': p3a, 'robust_five_hold_ge_8': p3b, 'failing_fields': fail, 'hold_counts': hold_counts,
               'rule': 'action_tendency, scope, need are the first to fail 5-of-9 (read: they are in the failing set) AND primary, valence, attribution, bodily_sensation, summary hold across >= 8 of 9'},
        'P4': {'held': sum(p4_arms.values()) >= 3, 'per_arm_null_ge_50pct': p4_arms, 'rule': 'intensity.value null on >= 50 % of texts for >= 3 of the 6 new arms'},
    }
    arm_stats = raw_arm_stats()
    json.dump({'counts': {m: dict(c) for m, c in counts.items()}, 'providers': {m: dict(p) for m, p in providers.items()}, 'texts_per_arm': {c: len(v) for c, v in by_arm.items()}, 'judged_units': len(judge),
               'thresholds': THRESH, 'units': UNITS, 'arms': ARMS, 'new_arms': NEW_ARMS, 'reference': REF, 'voter_rerun': SON, 'p1_set': P1_SET, 'bands': bands, 'predictions': predictions,
               'arm_stats': arm_stats, 'levers': J.LEVERS, 'table': table}, open(os.path.join(SCORING, 'field_table.json'), 'w', encoding='utf-8'), indent=1, default=str)
    # markdown summary
    def f(x): return '—' if x is None else f'{x:.2f}'
    short = {'google/gemini-4-argon': 'gemini', 'deepseek/deepseek-v4-pro-0813': 'deepseek', 'qwen/qwen3.8-2.4t-a95b': 'qwen', 'meta-llama/llama-4-maverick': 'llama', 'mistralai/mistral-large-4-0': 'mistral', 'openai/gpt-oss-120b': 'gpt-oss', REF: 'haiku', SON: 'sonnet-rerun'}
    L = ['# Run-3 scoring (generated by scripts/score.py)\n', f"Outputs: {json.dumps({m: dict(c) for m, c in counts.items()})}; judged (text, unit): {len(judge)}\n"]
    for scope in table:
        L.append(f'\n## {scope}\n')
        L.append('| Unit | shape | ' + ' | '.join(f'{short[m]} rep / agree / cov → decision' for m in ARMS) + ' | majority texts | framing | new hold | verdict |')
        L.append('|---|---|' + '---|' * len(ARMS) + '---|---|---|---|')
        for u, s, v in UNITS:
            r = table[scope][u]; cells = []
            for m in ARMS:
                a = r['arms'].get(m, {}); cells.append(f"{f(a.get('repeat'))} / {f(a.get('agree'))} / {f(a.get('coverage'))} → **{a.get('decision')}**" + (' ᵇ' if a.get('borderline') else '') + (' ˢ' if a.get('sparse') else ''))
            fr = r['framing']; frs = f(fr.get('kappa', fr.get('icc', fr.get('rate'))))
            L.append(f"| `{u}` | {s} | " + ' | '.join(cells) + f" | {r['majority'].get('texts_with_majority')} | {frs} | {r['verdict']['new_arms_hold']} of {r['verdict']['new_arms_run']} | {'**holds**' if r['verdict']['holds_across_market'] else '**FAILS 5-of-9**'} ({r['verdict']['total_hold']} of {r['verdict']['total_hold_of']}) |")
    L.append('\n## Bands (pooled)\n'); L.append('| Arm | repeat met / 19 | agree met / 19 | holds | repeats only | uncovered | band | P1 set |\n|---|---|---|---|---|---|---|---|')
    for m in ARMS:
        b = bands[m]; L.append(f"| `{m}` | {b['repeat_met']} | {b['agree_met']} | {b['holds']} | {b['repeats_only']} | {b['uncovered']} | {b['band']} | {'yes' if b['in_p1_set'] else ''} |")
    L.append('\n## Predictions\n'); L.extend(f"- **{k}**: {'held' if v['held'] else 'not held'} — {v['rule']}" for k, v in predictions.items())
    open(os.path.join(SCORING, 'field_table.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('scored; verdicts:', {FIELD_OF[u]: (P[u]['verdict']['total_hold'], P[u]['verdict']['holds_across_market']) for u, s, v in UNITS}); print('bands:', {short[m]: (bands[m]['repeat_met'], bands[m]['holds'], bands[m]['band']) for m in ARMS}); print('predictions:', {k: v['held'] for k, v in predictions.items()})


if __name__ == '__main__':
    main()
