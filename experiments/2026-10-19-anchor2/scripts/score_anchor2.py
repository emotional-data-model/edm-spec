"""Anchor-2 scoring (experiment-plan-anchor.md, Anchor-2 section, frozen). Per arm (A, B, C) and the anchor-1 raw records re-scored
under the same scheme as the "before" column: per model the modal `emotion.primary` label per comment over the valid repeats;
strict Cohen's kappa vs the human majority and vs each rater (>= 30 single-label items) and graded kappa (exact 1 / related 0.5 /
different 0), each at three grains (fine = EDM 35-word space via G2E35; ekman = GoEmotions 6 groups; valence = GoEmotions sentiment),
overall and on the seam subset; coverage; human-human rater-vs-rest range per grain; predictions P1-P4 and the disconfirmations;
exploratory per-word kappa / recall for the 18 additions. Writes scoring/anchor2_scoring.json and RESULTS.md.

Usage: python -P experiments/2026-10-19-anchor2/scripts/score_anchor2.py
"""
import json, os, sys, statistics
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP)
sys.path.insert(0, os.path.join(EXPS, '2026-10-17', 'scripts'))
from stats import fleiss_kappa  # noqa: E402
A1 = os.path.join(EXPS, '2026-10-18-anchor')
M = json.load(open(os.path.join(EXP, 'models_anchor2.json'), encoding='utf-8'))
MAP = json.load(open(os.path.join(EXP, 'mapping.json'), encoding='utf-8'))
V35 = MAP['vocabulary_v083'] + MAP['vocabulary_additions_mfoem']; ADD = MAP['vocabulary_additions_mfoem']
E2G = MAP['E2G']; G2E35 = MAP['G2E35']; SEAM = set(MAP['seam_labels'])
EKMAN = {l: g for g, ls in MAP['ekman'].items() for l in ls}; SENT = {l: s for s, ls in MAP['sentiment'].items() for l in ls}
EKSENT = MAP['ekman_sentiment']
HUMAN_RANGE_FROZEN = (0.25, 0.43)  # anchor-1 primary human-human IQR, as written in the plan
TOL = 0.05; MIN_RATER_ITEMS = 30
SHORT = {'SON': 'Claude Sonnet 5.5', 'GEM': 'Gemini 4 Argon', 'OSS': 'gpt-oss-120b'}
ARMS = ['A1'] + M['arm_order']; GRAINS = ['fine', 'ekman', 'valence']


# ---------- label spaces ----------
def norm(v):
    if v is None: return 'neutral'
    s = str(v).strip().lower()
    if s in ('', 'null', 'none', 'neutral'): return 'neutral'
    return s if s in V35 else 'other'


def h_fine(g): return G2E35[g]
def h_ekman(g): return 'neutral' if g == 'neutral' else EKMAN[g]
def h_val(g): return 'neutral' if g == 'neutral' else SENT[g]


def m_prim(w):
    if w in ('neutral', 'other'): return None
    return E2G[w]['primary']


def m_ekman(w):
    if w == 'neutral': return 'neutral'
    p = m_prim(w); return 'other' if p is None else EKMAN[p]


def m_val(w):
    if w == 'neutral': return 'neutral'
    p = m_prim(w); return 'other' if p is None else SENT[p]


HMAP = {'fine': h_fine, 'ekman': h_ekman, 'valence': h_val}; MMAP = {'fine': lambda w: w, 'ekman': m_ekman, 'valence': m_val}

# related pairs at the fine grain (mapping.json graded_related_rule)
REL_FINE = set()
for w, e in E2G.items():
    for g in ([e['primary']] if e['primary'] else []) + e['related']:
        x = G2E35.get(g)
        if x and x not in ('neutral', 'other') and x != w: REL_FINE.add(frozenset((w, x)))
for w1 in V35:
    for w2 in V35:
        p1, p2 = m_prim(w1), m_prim(w2)
        if w1 != w2 and p1 and p2 and EKMAN[p1] == EKMAN[p2]: REL_FINE.add(frozenset((w1, w2)))


def weight(grain, a, b):
    if a == b: return 1.0
    if a in ('neutral', 'other') or b in ('neutral', 'other'): return 0.0
    if grain == 'fine': return 0.5 if frozenset((a, b)) in REL_FINE else 0.0
    if grain == 'ekman': return 0.5 if EKSENT[a] == EKSENT[b] else 0.0
    return 0.5 if 'ambiguous' in (a, b) else 0.0


# ---------- statistics ----------
def cohen(pairs, grain=None):
    """strict when grain is None; graded (weighted) otherwise."""
    n = len(pairs)
    if n < 2: return None
    w = (lambda a, b: 1.0 if a == b else 0.0) if grain is None else (lambda a, b: weight(grain, a, b))
    po = sum(w(a, b) for a, b in pairs) / n
    ca = Counter(a for a, _ in pairs); cb = Counter(b for _, b in pairs)
    pe = sum(ca[x] * cb[y] * w(x, y) for x in ca for y in cb) / (n * n)
    if abs(1 - pe) < 1e-12: return 1.0 if abs(po - 1) < 1e-12 else None
    return (po - pe) / (1 - pe)


def quartiles(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    q = statistics.quantiles(xs, n=4, method='inclusive') if len(xs) >= 2 else [xs[0]] * 3
    return {'n': len(xs), 'min': xs[0], 'q1': q[0], 'median': q[1], 'q3': q[2], 'max': xs[-1]}


def modal(labels):
    c = Counter(labels); best = max(c.values())
    return next(l for l in labels if c[l] == best), (sum(1 for v in c.values() if v == best) > 1)


# ---------- data ----------
def load_arm(arm):
    """-> {model_key: {'per_item': {id: {repeat: raw_label}}, 'counts': {...}}}"""
    out = {}
    for k, e in M['extractors'].items():
        p = os.path.join(A1, 'raw', e['model'].replace('/', '__') + '.jsonl') if arm == 'A1' else os.path.join(EXP, 'raw', arm, e['model'].replace('/', '__') + '.jsonl')
        if not os.path.exists(p): continue
        per = defaultdict(dict); c = Counter()
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l); c['records'] += 1
            if r.get('transport_error'): c['transport'] += 1; continue
            c['calls'] += 1; c['usd'] += r.get('cost_usd') or 0; c['reasoning_tokens'] += (r.get('usage') or {}).get('reasoning_tokens') or 0
            c['prompt_tokens'] += ((r.get('usage') or {}).get('prompt_tokens_total') or ((r.get('usage') or {}).get('input_tokens') or 0) + ((r.get('usage') or {}).get('cached_input_tokens') or 0))
            if r.get('parse_error'): c['parse_fail'] += 1
            if r.get('provider_mismatch'): c['provider_mismatch'] += 1; continue
            for i, a in (r.get('answers') or {}).items(): per[i][r['repeat']] = (a or {}).get('primary')
            c['missing_ids'] += len(r['ids']) - len(r.get('answers') or {})
        out[k] = {'per_item': per, 'counts': dict(c)}
    return out


def human_side(sample, grain):
    hm = HMAP[grain]
    maj = {c['id']: hm(c['majority']) for c in sample}
    rater_items = defaultdict(dict)
    for c in sample:
        for rid, labs in c['raters'].items():
            if len(labs) == 1: rater_items[rid][c['id']] = hm(labs[0])
    raters = sorted(r for r in rater_items if len(rater_items[r]) >= MIN_RATER_ITEMS)
    by_id = {c['id']: c for c in sample}; rest = {}
    for r in raters:
        pairs = []
        for i, lab in rater_items[r].items():
            others = Counter(l for rid, labs in by_id[i]['raters'].items() if rid != r for l in labs)
            if not others: continue
            top = others.most_common()
            if top[0][1] < 2 or (len(top) > 1 and top[1][1] == top[0][1]): continue
            pairs.append((lab, hm(top[0][0])))
        if len(pairs) >= MIN_RATER_ITEMS: rest[r] = {'kappa': cohen(pairs), 'kappa_graded': cohen(pairs, grain), 'n': len(pairs)}
    return maj, rater_items, raters, rest


def score(sample, raw):
    seam_ids = {c['id'] for c in sample if c['majority'] in SEAM}
    H = {}
    for grain in GRAINS:
        maj, rater_items, raters, rest = human_side(sample, grain)
        H[grain] = {'maj': maj, 'rater_items': rater_items, 'raters': raters, 'rest': rest,
                    'range': quartiles([v['kappa'] for v in rest.values()]), 'range_graded': quartiles([v['kappa_graded'] for v in rest.values()])}
    R = {'human': {g: {'raters_scored': len(H[g]['rest']), 'rater_vs_rest_range': H[g]['range'], 'rater_vs_rest_range_graded': H[g]['range_graded'],
                       'majority_distribution': dict(Counter(H[g]['maj'].values()).most_common())} for g in GRAINS},
         'seam_n': len(seam_ids), 'arms': {}}
    for arm in ARMS:
        if arm not in raw: continue
        R['arms'][arm] = {}
        for k, d in raw[arm].items():
            per = d['per_item']; mod = {}; raw_mod = {}; ties = 0; rows = []
            for c in sample:
                labs = [per[c['id']][r] for r in sorted(per.get(c['id'], {}))]
                rows.append([norm(x) for x in labs])
                if not labs: continue
                rm, tie = modal([(str(x).strip().lower() if x is not None else 'null') for x in labs]); raw_mod[c['id']] = rm
                mod[c['id']], tie2 = modal([norm(x) for x in labs]); ties += tie2
            fk, finfo = fleiss_kappa(rows); fk = 1.0 if (fk is None and finfo.get('P_bar') == 1.0) else fk
            res = {'coverage': len(mod), 'coverage_rate': len(mod) / len(sample), 'modal_ties': ties, 'repeat_fleiss_fine': fk, 'counts': d['counts'],
                   'modal_distribution_fine': dict(Counter(mod.values()).most_common()), 'raw_modal_distribution': dict(Counter(raw_mod.values()).most_common(40)), 'grains': {}}
            for grain in GRAINS:
                mm = MMAP[grain]; maj = H[grain]['maj']
                ml = {i: mm(w) for i, w in mod.items()}
                g = {}
                for scope, ids in (('overall', set(ml)), ('seam', set(ml) & seam_ids), ('off_seam', set(ml) - seam_ids)):
                    pairs = [(ml[i], maj[i]) for i in sorted(ids)]
                    g[scope] = {'n': len(pairs), 'strict': cohen(pairs), 'graded': cohen(pairs, grain), 'raw_agreement': (sum(1 for a, b in pairs if a == b) / len(pairs)) if pairs else None}
                vs_r = {}
                for r in H[grain]['raters']:
                    pr = [(ml[i], lab) for i, lab in H[grain]['rater_items'][r].items() if i in ml]
                    if len(pr) >= MIN_RATER_ITEMS: vs_r[r] = {'strict': cohen(pr), 'graded': cohen(pr, grain), 'n': len(pr)}
                g['vs_rater'] = {'n_raters': len(vs_r), 'strict_quartiles': quartiles([v['strict'] for v in vs_r.values()]), 'graded_quartiles': quartiles([v['graded'] for v in vs_r.values()])}
                conf = Counter((maj[i], ml[i]) for i in ml)
                g['top_confusions_human_to_model'] = [{'human': h, 'model': m, 'n': n} for (h, m), n in conf.most_common(80) if h != m][:12]
                res['grains'][grain] = g
            # exploratory per-word for the additions (fine grain, binary category kappa and recall, as R31)
            fm = H['fine']['maj']; pw = {}
            for w in ADD:
                pairs = [(fm[i] == w, mod[i] == w) for i in mod]; n_h = sum(1 for a, _ in pairs if a)
                hit = [b for a, b in pairs if a]; used = sum(1 for _, b in pairs if b)
                pw[w] = {'n_human': n_h, 'n_model_modal': used, 'kappa': cohen(pairs) if n_h else None, 'recall': (sum(hit) / len(hit)) if hit else None,
                         'precision': (sum(1 for a, b in pairs if a and b) / used) if used else None}
            res['additions_per_word'] = pw
            R['arms'][arm][k] = res
    return R


def predictions(R):
    ks = [k for k in ('SON', 'GEM', 'OSS') if k in R['arms'].get('A', {})]
    def kap(arm, k, grain='fine', scope='overall', kind='strict'):
        return (((R['arms'].get(arm) or {}).get(k) or {}).get('grains') or {}).get(grain, {}).get(scope, {}).get(kind)
    def ok(x): return x is not None
    lo, hi = HUMAN_RANGE_FROZEN
    p1_in = {k: (ok(kap('A', k)) and lo <= kap('A', k) <= hi) for k in ks}
    p1_seam = {}
    for k in ks:
        a_s, b_s, a_o, b_o = kap('A', k, scope='seam'), kap('A1', k, scope='seam'), kap('A', k, scope='off_seam'), kap('A1', k, scope='off_seam')
        p1_seam[k] = (all(ok(x) for x in (a_s, b_s, a_o, b_o)) and (a_s - b_s) > (a_o - b_o))
    P1 = {'rule': 'arm A fine strict kappa vs majority within [0.25, 0.43] for >= 2 of 3 models, and seam lift (A - before) > off-seam lift for >= 2 of 3',
          'in_range': p1_in, 'seam_lift_exceeds_off_seam': p1_seam, 'kappa_A': {k: kap('A', k) for k in ks}, 'kappa_before': {k: kap('A1', k) for k in ks},
          'held': sum(p1_in.values()) >= 2 and sum(p1_seam.values()) >= 2}
    p2 = {}
    for k in ks:
        a, b, c = kap('A', k, scope='seam'), kap('B', k, scope='seam'), kap('C', k, scope='seam')
        p2[k] = all(ok(x) for x in (a, b, c)) and (b - max(a, c) >= TOL) and abs(c - a) <= TOL
    P2 = {'rule': f'seam subset, fine strict: B exceeds both A and C by >= {TOL} and |C - A| <= {TOL}, for >= 2 of 3 models', 'per_model': p2,
          'seam_kappa': {k: {arm: kap(arm, k, scope='seam') for arm in ('A1', 'A', 'B', 'C')} for k in ks}, 'held': sum(p2.values()) >= 2}
    p3 = {}; p3_cells = {}
    for k in ks:
        cells = {}
        for grain in GRAINS:
            for scope in ('overall', 'seam'):
                a, c = kap('A', k, grain, scope), kap('C', k, grain, scope)
                cells[f'{grain}/{scope}'] = (abs(c - a) if (ok(a) and ok(c)) else None)
        p3_cells[k] = cells; p3[k] = all(v is not None and v <= TOL for v in cells.values())
    P3 = {'rule': f'|C - A| <= {TOL} strict at every grain, overall and seam, for every model', 'per_model': p3, 'abs_diff': p3_cells, 'held': bool(ks) and all(p3.values())}
    p4 = {}
    for arm in ('A', 'B', 'C'):
        for k in ks:
            for grain in GRAINS:
                s, g = kap(arm, k, grain, 'overall', 'strict'), kap(arm, k, grain, 'overall', 'graded')
                p4[f'{arm}/{k}/{grain}'] = (ok(s) and ok(g) and g > s)
    P4 = {'rule': 'graded kappa > strict kappa at every grain, every arm and model (overall)', 'cells': p4, 'held': bool(p4) and all(p4.values())}
    # disconfirmations
    d = {}
    d['length_not_reading'] = {'rule': f'|B - C| <= {TOL} on the seam subset (fine strict) for >= 2 of 3 models: the B lift is prompt length', 'per_model': {k: (ok(kap('B', k, scope='seam')) and ok(kap('C', k, scope='seam')) and abs(kap('B', k, scope='seam') - kap('C', k, scope='seam')) <= TOL) for k in ks}}
    d['length_not_reading']['triggered'] = sum(d['length_not_reading']['per_model'].values()) >= 2
    d['priming'] = {'rule': f'B - A >= {TOL} off the seams and the off-seam lift >= the seam lift (fine strict), for >= 2 of 3 models: priming, not reading',
                    'per_model': {k: (all(ok(kap(arm, k, scope=s)) for arm in ('A', 'B') for s in ('seam', 'off_seam')) and (kap('B', k, scope='off_seam') - kap('A', k, scope='off_seam') >= TOL) and (kap('B', k, scope='off_seam') - kap('A', k, scope='off_seam')) >= (kap('B', k, scope='seam') - kap('A', k, scope='seam'))) for k in ks}}
    d['priming']['triggered'] = sum(d['priming']['per_model'].values()) >= 2
    d['flat_B'] = {'rule': f'|B - A| <= {TOL} strict at every grain, overall and seam, for every model: evidence about content cues on this corpus only, not about the catalogue',
                   'per_model': {k: all((ok(kap('A', k, g, s)) and ok(kap('B', k, g, s)) and abs(kap('B', k, g, s) - kap('A', k, g, s)) <= TOL) for g in GRAINS for s in ('overall', 'seam')) for k in ks}}
    d['flat_B']['triggered'] = bool(ks) and all(d['flat_B']['per_model'].values())
    return {'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4}, d


def main():
    sample = json.load(open(os.path.join(A1, 'data', 'sample.json'), encoding='utf-8'))
    raw = {arm: load_arm(arm) for arm in ARMS}; raw = {a: r for a, r in raw.items() if r}
    R = score(sample, raw); P, D = predictions(R)
    spend = json.load(open(os.path.join(EXP, 'spend_anchor2.json'), encoding='utf-8')) if os.path.exists(os.path.join(EXP, 'spend_anchor2.json')) else {'total_usd': 0, 'calls': 0, 'by_arm': {}}
    lev = json.load(open(os.path.join(EXP, 'levers_anchor2.json'), encoding='utf-8')) if os.path.exists(os.path.join(EXP, 'levers_anchor2.json')) else {}
    os.makedirs(os.path.join(EXP, 'scoring'), exist_ok=True)
    json.dump({'spend': spend, 'levers': lev, 'human_range_frozen': HUMAN_RANGE_FROZEN, 'tolerance': TOL, 'results': R, 'predictions': P, 'disconfirmations': D},
              open(os.path.join(EXP, 'scoring', 'anchor2_scoring.json'), 'w', encoding='utf-8'), indent=1, default=str)

    def f(x, d=2): return '—' if x is None else f'{x:.{d}f}'
    arms = [a for a in ARMS if a in R['arms']]; ks = [k for k in ('SON', 'GEM', 'OSS') if any(k in R['arms'][a] for a in arms)]
    AN = {'A1': 'before (anchor-1)', 'A': 'A wider vocab', 'B': 'B + cues', 'C': 'C + control'}
    L = ['# RESULTS — anchor-2: wider vocabulary, content cues, prompt-length control (2026-10-19)\n',
         'Generated by `scripts/score_anchor2.py` from `raw/<arm>/*.jsonl`, the anchor-1 raw records (before column, re-scored under the anchor-2 scheme), `mapping.json`, `spend_anchor2.json`. Pre-registration: `docs/discovery/ontology-crosswalk-2026-10/experiment-plan-anchor.md`, Anchor-2 section, frozen before any call. No re-classification after the run.\n']
    L.append(f"**Run.** 1,000 GoEmotions comments, 3 extractors × 3 repeats per arm, `emotion.primary` only. Calls {spend.get('calls', 0)}, **spend USD {spend.get('total_usd', 0):.2f}** against the hard cap USD {M['cap_usd']}" + (' (' + '; '.join(f"arm {a}: USD {v['usd']:.2f}, {v['calls']} calls" for a, v in (spend.get('by_arm') or {}).items()) + ')' if spend.get('by_arm') else '') + '.\n')
    L.append('Per arm and extractor: ' + '; '.join(f"{a}/{SHORT[k]} calls {R['arms'][a][k]['counts'].get('calls', 0)}, parse fail {R['arms'][a][k]['counts'].get('parse_fail', 0)}, missing ids {R['arms'][a][k]['counts'].get('missing_ids', 0)}, transport {R['arms'][a][k]['counts'].get('transport', 0)}, mismatch {R['arms'][a][k]['counts'].get('provider_mismatch', 0)}, coverage {R['arms'][a][k]['coverage']}, mean prompt tokens {f(R['arms'][a][k]['counts'].get('prompt_tokens', 0) / max(1, R['arms'][a][k]['counts'].get('calls', 1)), 0)}" for a in arms for k in ks if k in R['arms'][a]) + '.\n')
    def kk(arm, k, scope='overall'): return f(((R['arms'].get(arm) or {}).get(k) or {}).get('grains', {}).get('fine', {}).get(scope, {}).get('strict'))
    L.append('## 0. Verdict\n')
    L.append(f"**P1 {'held' if P['P1']['held'] else 'failed'}, P2 {'held' if P['P2']['held'] else 'failed'}, P3 {'held' if P['P3']['held'] else 'failed'}, P4 {'held' if P['P4']['held'] else 'failed'}.** Fine-grain strict κ vs the human majority, before → A / B / C: " + '; '.join(f"{SHORT[k]} {kk('A1', k)} → {kk('A', k)} / {kk('B', k)} / {kk('C', k)} (seam {kk('A1', k, 'seam')} → {kk('A', k, 'seam')} / {kk('B', k, 'seam')} / {kk('C', k, 'seam')}; off-seam {kk('A1', k, 'off_seam')} → {kk('A', k, 'off_seam')} / {kk('B', k, 'off_seam')} / {kk('C', k, 'off_seam')})" for k in ks) + f". Disconfirmations triggered: {', '.join(k for k, v in D.items() if v['triggered']) or 'none'}.\n")
    L.append('## 1. Predictions (frozen)\n')
    L.append('| # | Rule | Result | Evidence |\n|---|---|---|---|')
    for pk, pv in P.items(): L.append(f"| {pk} | {pv['rule']} | **{'held' if pv['held'] else 'failed'}** | {json.dumps({kk: vv for kk, vv in pv.items() if kk not in ('held', 'rule')}, default=lambda x: round(x, 3) if isinstance(x, float) else x)} |")
    L.append('\nDisconfirmations (frozen):\n')
    L.append('| Reading | Rule | Triggered | Per model |\n|---|---|---|---|')
    for dk, dv in D.items(): L.append(f"| {dk} | {dv['rule']} | **{'yes' if dv['triggered'] else 'no'}** | {dv['per_model']} |")
    L.append('\n## 2. Human–human range per grain (rater vs rest, raters with ≥ 30 single-label items)\n')
    L.append('| Grain | raters | strict [Q1, Q3] (median; min–max) | graded [Q1, Q3] (median) |\n|---|---|---|---|')
    for g in GRAINS:
        h = R['human'][g]; q = h['rater_vs_rest_range'] or {}; qg = h['rater_vs_rest_range_graded'] or {}
        L.append(f"| {g} | {h['raters_scored']} | [{f(q.get('q1'))}, {f(q.get('q3'))}] ({f(q.get('median'))}; {f(q.get('min'))}–{f(q.get('max'))}) | [{f(qg.get('q1'))}, {f(qg.get('q3'))}] ({f(qg.get('median'))}) |")
    L.append(f"\nThe plan's P1 uses the frozen anchor-1 range [{HUMAN_RANGE_FROZEN[0]:.2f}, {HUMAN_RANGE_FROZEN[1]:.2f}] (17-word G2E, 19 categories); the fine-grain range above is the same raters re-scored in the 35-word space.\n")
    L.append('## 3. Before / after per model per arm: κ vs human majority\n')
    for grain in GRAINS:
        L.append(f'### Grain: {grain}\n')
        L.append('| Model | Arm | n | strict overall | graded overall | strict seam | graded seam | strict off-seam | vs rater strict median [IQR] | raw agr |\n|---|---|---|---|---|---|---|---|---|---|')
        for k in ks:
            for a in arms:
                if k not in R['arms'][a]: continue
                g = R['arms'][a][k]['grains'][grain]; vq = g['vs_rater']['strict_quartiles'] or {}
                L.append(f"| {SHORT[k]} | {AN[a]} | {g['overall']['n']} | {f(g['overall']['strict'])} | {f(g['overall']['graded'])} | {f(g['seam']['strict'])} | {f(g['seam']['graded'])} | {f(g['off_seam']['strict'])} | {f(vq.get('median'))} [{f(vq.get('q1'))}, {f(vq.get('q3'))}] ({g['vs_rater']['n_raters']}) | {f(g['overall']['raw_agreement'])} |")
        L.append('')
    L.append(f"Seam subset: {R['seam_n']} comments whose human majority is one of {sorted(SEAM)}.\n")
    L.append('## 4. Repeatability, coverage, modal distributions (fine grain)\n')
    L.append('| Model | Arm | coverage | Fleiss κ (3 repeats) | modal ties | top modal labels |\n|---|---|---|---|---|---|')
    for k in ks:
        for a in arms:
            if k not in R['arms'][a]: continue
            r = R['arms'][a][k]
            L.append(f"| {SHORT[k]} | {AN[a]} | {r['coverage']} | {f(r['repeat_fleiss_fine'])} | {r['modal_ties']} | {', '.join(f'{l} {n}' for l, n in list(r['modal_distribution_fine'].items())[:10])} |")
    L.append('\n## 5. Largest human → model confusions (fine grain, modal vs majority)\n')
    for a in arms:
        for k in ks:
            if k in R['arms'][a]: L.append(f"- **{AN[a]} / {SHORT[k]}:** " + '; '.join(f"{x['human']} → {x['model']} ({x['n']})" for x in R['arms'][a][k]['grains']['fine']['top_confusions_human_to_model'][:10]))
    L.append('\n## 6. Exploratory: the 18 additions per word (fine grain; binary category κ and recall vs the G2E35 human side; not pre-registered as a test, recorded for a later ranking)\n')
    L.append('| Word | human n | ' + ' | '.join(f'{AN[a]} / {SHORT[k]} κ / recall / used' for a in arms if a != 'A1' for k in ks if k in R['arms'][a]) + ' |\n|---|---|' + '---|' * sum(1 for a in arms if a != 'A1' for k in ks if k in R['arms'][a]))
    for w in ADD:
        n_h = next((R['arms'][a][k]['additions_per_word'][w]['n_human'] for a in arms for k in ks if k in R['arms'][a]), 0)
        L.append(f"| {w} | {n_h} | " + ' | '.join(f"{f(R['arms'][a][k]['additions_per_word'][w]['kappa'])} / {f(R['arms'][a][k]['additions_per_word'][w]['recall'])} / {R['arms'][a][k]['additions_per_word'][w]['n_model_modal']}" for a in arms if a != 'A1' for k in ks if k in R['arms'][a]) + ' |')
    L.append('\n## 7. Deviations\n')
    L.append(json.dumps(lev, indent=1) if lev else 'None.')
    L.append('')
    open(os.path.join(EXP, 'RESULTS.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('predictions:', {k: v['held'] for k, v in P.items()}, 'disconfirmations:', {k: v['triggered'] for k, v in D.items()})
    for k in ks: print(k, {a: (f(R['arms'][a][k]['grains']['fine']['overall']['strict']), f(R['arms'][a][k]['grains']['fine']['seam']['strict'])) for a in arms if k in R['arms'][a]})
    print('spend USD', f(spend.get('total_usd', 0)))


if __name__ == '__main__':
    main()
