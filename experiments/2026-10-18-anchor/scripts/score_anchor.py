"""Human-anchor scoring (experiment-plan-anchor.md section 5): per model, modal label per comment over the valid repeats;
kappa against the human majority (G2E-mapped), against each rater (single-label annotations, >= 30 per rater), the
human rater-vs-rest kappa whose interquartile range is the human-human range, the pairwise pooled rater kappa, Fleiss'
repeatability over the repeats; the same for valence collapsed through the GoEmotions sentiment grouping. Writes
scoring/anchor_scoring.json and RESULTS.md with the pre-registered sentence per field and model.

Usage: python -P experiments/2026-10-18-anchor/scripts/score_anchor.py
"""
import json, os, sys, statistics
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP)
sys.path.insert(0, os.path.join(EXPS, '2026-10-17', 'scripts'))
from stats import fleiss_kappa  # noqa: E402
M = json.load(open(os.path.join(EXP, 'models_anchor.json'), encoding='utf-8'))
EDM17 = ['anger', 'anxiety', 'disappointment', 'fear', 'frustration', 'gratitude', 'hope', 'joy', 'longing', 'peace', 'pride', 'relief', 'reverence', 'sadness', 'shame', 'tenderness', 'wonder']
# frozen mapping GoEmotions -> EDM emotion.primary (plan section 3; crosswalk row constellation.emotion_primary)
G2E = {'joy': 'joy', 'sadness': 'sadness', 'fear': 'fear', 'anger': 'anger', 'pride': 'pride', 'gratitude': 'gratitude', 'relief': 'relief', 'disappointment': 'disappointment',
       'nervousness': 'anxiety', 'optimism': 'hope', 'desire': 'longing', 'surprise': 'wonder', 'curiosity': 'wonder', 'admiration': 'reverence', 'caring': 'tenderness', 'love': 'tenderness',
       'embarrassment': 'shame', 'remorse': 'shame', 'annoyance': 'frustration', 'neutral': 'neutral',
       'amusement': 'other', 'approval': 'other', 'confusion': 'other', 'disapproval': 'other', 'disgust': 'other', 'excitement': 'other', 'grief': 'other', 'realization': 'other'}
SENT = {'positive': ['amusement', 'excitement', 'joy', 'love', 'desire', 'optimism', 'caring', 'pride', 'admiration', 'gratitude', 'relief', 'approval'],
        'negative': ['fear', 'nervousness', 'remorse', 'embarrassment', 'disappointment', 'sadness', 'grief', 'disgust', 'anger', 'annoyance', 'disapproval'],
        'mixed': ['realization', 'surprise', 'curiosity', 'confusion'], 'neutral': ['neutral']}
G2V = {l: s for s, ls in SENT.items() for l in ls}
MIN_RATER_ITEMS = 30
SHORT = {k: e['slot'] for k, e in M['extractors'].items()}


def norm_primary(v):
    if v is None: return 'neutral'
    s = str(v).strip().lower()
    if s in ('', 'null', 'none', 'neutral'): return 'neutral'
    return s if s in EDM17 else 'other'


def norm_valence(v):
    if v is None: return 'neutral'
    s = str(v).strip().lower()
    if s in ('', 'null', 'none', 'neutral'): return 'neutral'
    return s if s in ('positive', 'negative', 'mixed') else 'other'


def cohen(pairs):
    n = len(pairs)
    if n < 2: return None, None, n
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, b in pairs); cb = Counter(b for a, b in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if abs(1 - pe) < 1e-12: return (1.0 if po == 1.0 else None), po, n
    return (po - pe) / (1 - pe), po, n


def modal(labels):
    c = Counter(labels); best = max(c.values())
    return next(l for l in labels if c[l] == best), (sum(1 for v in c.values() if v == best) > 1)


def quartiles(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    q = statistics.quantiles(xs, n=4, method='inclusive') if len(xs) >= 2 else [xs[0], xs[0], xs[0]]
    return {'n': len(xs), 'min': xs[0], 'q1': q[0], 'median': q[1], 'q3': q[2], 'max': xs[-1]}


def load_raw():
    out = {}
    for k, e in M['extractors'].items():
        p = os.path.join(EXP, 'raw', e['model'].replace('/', '__') + '.jsonl'); per = defaultdict(dict); c = Counter()
        if not os.path.exists(p): continue
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l); c['records'] += 1
            if r.get('transport_error'): c['transport'] += 1; continue
            c['calls'] += 1; c['usd'] += r.get('cost_usd') or 0; c['reasoning_tokens'] += (r.get('usage') or {}).get('reasoning_tokens') or 0
            if r.get('parse_error'): c['parse_fail'] += 1
            if r.get('provider_mismatch'): c['provider_mismatch'] += 1; continue
            for i, a in (r.get('answers') or {}).items(): per[i][r['repeat']] = a  # last record per (repeat, batch) wins
            c['missing_ids'] += len(r['ids']) - len(r.get('answers') or {})
        out[k] = {'per_item': per, 'counts': dict(c)}
    return out


def score_field(field, sample, raw, hum_label, mod_label):
    """field: 'primary' | 'valence'; hum_label(goemotions label) -> category; mod_label(answer dict) -> category."""
    res = {'models': {}, 'human': {}}
    maj = {c['id']: hum_label(c['majority']) for c in sample}
    # rater single-label annotations
    rater_items = defaultdict(dict)
    for c in sample:
        for rid, labs in c['raters'].items():
            if len(labs) == 1: rater_items[rid][c['id']] = hum_label(labs[0])
    raters = sorted(r for r in rater_items if len(rater_items[r]) >= MIN_RATER_ITEMS)
    # rater vs rest
    rest = {}; pooled_rest = []
    by_id = {c['id']: c for c in sample}
    for r in raters:
        pairs = []
        for i, lab in rater_items[r].items():
            others = Counter(l for rid, labs in by_id[i]['raters'].items() if rid != r for l in labs)
            if not others: continue
            top = others.most_common()
            if top[0][1] < 2 or (len(top) > 1 and top[1][1] == top[0][1]): continue
            pairs.append((lab, hum_label(top[0][0])))
        if len(pairs) >= MIN_RATER_ITEMS:
            k, po, n = cohen(pairs); rest[r] = {'kappa': k, 'raw': po, 'n': n}; pooled_rest.extend(pairs)
    kq = quartiles([v['kappa'] for v in rest.values()])
    kp, pp, np_ = cohen(pooled_rest)
    # pairwise
    pair_pairs = defaultdict(list)
    for c in sample:
        singles = [(rid, hum_label(labs[0])) for rid, labs in sorted(c['raters'].items()) if len(labs) == 1]
        for x in range(len(singles)):
            for y in range(x + 1, len(singles)):
                pair_pairs[(singles[x][0], singles[y][0])].append((singles[x][1], singles[y][1]))
    all_pairs = [p for ps in pair_pairs.values() for p in ps]
    kpair, ppair, npair = cohen(all_pairs)
    pair_dist = quartiles([cohen(ps)[0] for ps in pair_pairs.values() if len(ps) >= MIN_RATER_ITEMS])
    res['human'] = {'raters_scored': len(rest), 'rater_vs_rest': {r: rest[r] for r in rest}, 'rater_vs_rest_quartiles': kq, 'rater_vs_rest_pooled': {'kappa': kp, 'raw': pp, 'n': np_},
                    'pairwise_pooled': {'kappa': kpair, 'raw': ppair, 'n': npair, 'pairs': len(pair_pairs)}, 'pairwise_quartiles_pairs_ge_30': pair_dist,
                    'majority_distribution': dict(Counter(maj.values()).most_common())}
    for k, d in raw.items():
        per = d['per_item']; mod = {}; ties = 0; nolabel = 0; rows = []
        for c in sample:
            labs = [mod_label(a) for rep, a in sorted(per.get(c['id'], {}).items())]
            rows.append(labs)
            if not labs: nolabel += 1; continue
            m, tie = modal(labs); mod[c['id']] = m; ties += tie
        fk, finfo = fleiss_kappa(rows); fk = 1.0 if (fk is None and finfo.get('P_bar') == 1.0) else fk
        pairs = [(mod[i], maj[i]) for i in mod]
        kmaj, raw_maj, n = cohen(pairs)
        vs_r = {}
        for r in raters:
            pr = [(mod[i], lab) for i, lab in rater_items[r].items() if i in mod]
            if len(pr) >= MIN_RATER_ITEMS: kk, po, nn = cohen(pr); vs_r[r] = {'kappa': kk, 'raw': po, 'n': nn}
        vq = quartiles([v['kappa'] for v in vs_r.values()])
        if kq is None or kmaj is None: sentence = 'undetermined'
        elif kmaj < kq['q1']: sentence = 'below'
        elif kmaj > kq['q3']: sentence = 'above'
        else: sentence = 'within'
        conf = Counter((maj[i], mod[i]) for i in mod)
        res['models'][k] = {'kappa_majority': kmaj, 'raw_majority': raw_maj, 'n_items': n, 'items_without_label': nolabel, 'modal_ties': ties, 'repeat_fleiss': fk, 'repeat_subjects': finfo.get('subjects'),
                            'vs_rater': vs_r, 'vs_rater_quartiles': vq, 'sentence': sentence, 'modal_distribution': dict(Counter(mod.values()).most_common()),
                            'top_confusions_human_to_model': [{'human': h, 'model': m, 'n': c} for (h, m), c in conf.most_common(60) if h != m][:15]}
    return res


def main():
    sample = json.load(open(os.path.join(EXP, 'data', 'sample.json'), encoding='utf-8')); raw = load_raw()
    spend = json.load(open(os.path.join(EXP, 'spend_anchor.json'), encoding='utf-8')) if os.path.exists(os.path.join(EXP, 'spend_anchor.json')) else {'total_usd': 0, 'calls': 0}
    lev = json.load(open(os.path.join(EXP, 'levers_anchor.json'), encoding='utf-8')) if os.path.exists(os.path.join(EXP, 'levers_anchor.json')) else {}
    R = {'primary': score_field('primary', sample, raw, lambda g: G2E[g], lambda a: norm_primary(a.get('primary'))),
         'valence': score_field('valence', sample, raw, lambda g: G2V[g], lambda a: norm_valence(a.get('valence')))}
    # predictions
    P = R['primary']['models']; V = R['valence']['models']; keys = list(raw)
    hq_p = R['primary']['human']['rater_vs_rest_quartiles']; hq_v = R['valence']['human']['rater_vs_rest_quartiles']
    order = ['SON', 'GEM', 'OSS']; ks = [k for k in order if k in P]
    pred = {'P1': {'held': bool(ks) and all(P[k]['sentence'] == 'below' for k in ks), 'per_model': {k: P[k]['sentence'] for k in ks}, 'rule': 'primary: every model below the human-human range'},
            'P2': {'held': bool(ks) and all(V[k]['sentence'] in ('within', 'above') for k in ks), 'per_model': {k: V[k]['sentence'] for k in ks}, 'rule': 'valence: every model within or above the range'},
            'P3': {'held': len(ks) == 3 and (P['SON']['kappa_majority'] or -9) >= (P['GEM']['kappa_majority'] or -9) >= (P['OSS']['kappa_majority'] or -9), 'kappas': {k: P[k]['kappa_majority'] for k in ks}, 'rule': 'primary kappa_majority: SON >= GEM >= OSS'},
            'P4': {'held': all((P[k]['repeat_fleiss'] or 0) >= 0.70 for k in ks if k in ('SON', 'GEM')) and any(k in ks for k in ('SON', 'GEM')), 'fleiss': {k: P[k]['repeat_fleiss'] for k in ks}, 'rule': 'primary repeatability >= 0.70 for SON and GEM'},
            'P5': {'held': bool(ks) and all((P[k]['vs_rater_quartiles'] or {}).get('median', 9) < (hq_p or {}).get('median', -9) for k in ks) and any((V[k]['vs_rater_quartiles'] or {}).get('median', -9) >= (hq_v or {}).get('median', 9) for k in ks),
                   'primary_medians': {k: (P[k]['vs_rater_quartiles'] or {}).get('median') for k in ks}, 'valence_medians': {k: (V[k]['vs_rater_quartiles'] or {}).get('median') for k in ks},
                   'human_medians': {'primary': (hq_p or {}).get('median'), 'valence': (hq_v or {}).get('median')}, 'rule': 'vs-rater median below the rater-vs-rest median for every model on primary, not below for >= 1 model on valence'}}
    os.makedirs(os.path.join(EXP, 'scoring'), exist_ok=True)
    json.dump({'counts': {k: raw[k]['counts'] for k in raw}, 'spend': spend, 'levers': lev, 'mapping_G2E': G2E, 'sentiment': SENT, 'min_rater_items': MIN_RATER_ITEMS, 'fields': R, 'predictions': pred},
              open(os.path.join(EXP, 'scoring', 'anchor_scoring.json'), 'w', encoding='utf-8'), indent=1, default=str)

    def f(x): return '—' if x is None else f'{x:.2f}'
    L = ['# RESULTS — human anchor on GoEmotions (2026-10-18)\n',
         'Generated by `scripts/score_anchor.py` from `raw/*.jsonl`, `data/sample.json`, `spend_anchor.json`. Pre-registration: `docs/discovery/ontology-crosswalk-2026-10/experiment-plan-anchor.md`, frozen before any call. Mapping, thresholds and the sentence rule are the frozen ones. Nothing pushed; the founder\'s archive is not used.\n']
    n_calls = sum(raw[k]['counts'].get('calls', 0) for k in raw)
    L.append(f"**Run.** 1,000 GoEmotions comments (stratified by human majority label; 82 raters in the release), 3 extractors × 3 repeats in batches of 20: {n_calls} billed calls, **USD {spend['total_usd']:.2f}** against the cap USD {M['cap_usd']}. " + '; '.join(f"{SHORT[k]}: {raw[k]['counts'].get('calls', 0)} calls, parse fail {raw[k]['counts'].get('parse_fail', 0)}, missing ids {raw[k]['counts'].get('missing_ids', 0)}, transport {raw[k]['counts'].get('transport', 0)}, provider mismatch {raw[k]['counts'].get('provider_mismatch', 0)}, USD {raw[k]['counts'].get('usd', 0):.2f}" for k in raw) + '.\n')
    L.append('## 1. The sentence per field\n')
    for field, name in (('primary', '`emotion.primary` (19-category space: 17 EDM values + neutral + other)'), ('valence', '`emotion.valence` (positive / negative / mixed / neutral)')):
        h = R[field]['human']; q = h['rater_vs_rest_quartiles'] or {}
        L.append(f"**{name}.** Human–human range (rater-vs-rest κ, {h['raters_scored']} raters with ≥ {MIN_RATER_ITEMS} single-label items): **[{f(q.get('q1'))}, {f(q.get('q3'))}]** (median {f(q.get('median'))}, min {f(q.get('min'))}, max {f(q.get('max'))}; pooled {f(h['rater_vs_rest_pooled']['kappa'])} over {h['rater_vs_rest_pooled']['n']} pairs; pairwise pooled κ {f(h['pairwise_pooled']['kappa'])} over {h['pairwise_pooled']['n']} rater-pair items).\n")
        for k in ks:
            m = R[field]['models'][k]
            L.append(f"- **{SHORT[k]}: model–human κ is {m['sentence']} the human–human range** — κ vs majority {f(m['kappa_majority'])} (raw {f(m['raw_majority'])}, n {m['n_items']}); vs each rater median {f((m['vs_rater_quartiles'] or {}).get('median'))} [IQR {f((m['vs_rater_quartiles'] or {}).get('q1'))}, {f((m['vs_rater_quartiles'] or {}).get('q3'))}] over {len(m['vs_rater'])} raters; repeatability Fleiss κ {f(m['repeat_fleiss'])}; modal ties {m['modal_ties']}; items without a label {m['items_without_label']}.")
        L.append('')
    L.append('## 2. Predictions (frozen)\n')
    L.append('| # | Prediction | Result | Evidence |\n|---|---|---|---|')
    for pk, pv in pred.items(): L.append(f"| {pk} | {pv['rule']} | **{'held' if pv['held'] else 'not held'}** | {json.dumps({kk: vv for kk, vv in pv.items() if kk not in ('held', 'rule')}, default=lambda x: round(x, 3) if isinstance(x, float) else x)} |")
    L.append('\n## 3. Human majority distribution and the models\' modal distributions (`primary`)\n')
    L.append('| Category | human majority | ' + ' | '.join(SHORT[k] for k in ks) + ' |\n|---|---|' + '---|' * len(ks))
    cats = sorted(set(R['primary']['human']['majority_distribution']) | {c for k in ks for c in R['primary']['models'][k]['modal_distribution']})
    for c in cats: L.append(f"| {c} | {R['primary']['human']['majority_distribution'].get(c, 0)} | " + ' | '.join(str(R['primary']['models'][k]['modal_distribution'].get(c, 0)) for k in ks) + ' |')
    L.append('\n## 4. Largest human → model confusions (`primary`, modal label vs majority)\n')
    for k in ks:
        L.append(f"- **{SHORT[k]}:** " + '; '.join(f"{x['human']} → {x['model']} ({x['n']})" for x in R['primary']['models'][k]['top_confusions_human_to_model'][:10]))
    L.append('\n## 5. Valence detail\n')
    L.append('| Model | κ vs majority | raw | vs rater median [IQR] | Fleiss κ |\n|---|---|---|---|---|')
    for k in ks:
        m = R['valence']['models'][k]; vq = m['vs_rater_quartiles'] or {}
        L.append(f"| {SHORT[k]} | {f(m['kappa_majority'])} | {f(m['raw_majority'])} | {f(vq.get('median'))} [{f(vq.get('q1'))}, {f(vq.get('q3'))}] | {f(m['repeat_fleiss'])} |")
    L.append('\n## 6. Deviations\n')
    L.append(json.dumps(lev, indent=1) if lev else 'None.')
    L.append('')
    open(os.path.join(EXP, 'RESULTS.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print('scored:', {k: (f(P[k]['kappa_majority']), P[k]['sentence'], f(V[k]['kappa_majority']), V[k]['sentence']) for k in ks}, 'human primary', {kk: f(vv) for kk, vv in (hq_p or {}).items()}, 'valence', {kk: f(vv) for kk, vv in (hq_v or {}).items()})
    print('predictions:', {k: v['held'] for k, v in pred.items()})


if __name__ == '__main__':
    main()
