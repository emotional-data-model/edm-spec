"""Descriptive diagnostics (experiment-plan.md sections 4.4 and 4.5): null precision on the synthetic arm, event_category
accuracy, dimension-value distributions per extractor, trait-language leakage. No API calls.
Usage: python -P experiments/2026-10-17/scripts/diagnostics.py -> scoring/diagnostics.{json,md}
"""
import json, os, sys, re, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from score import load_outputs, get_unit, norm_label, norm_text, num, EXTRACTORS, EXP, SCORING  # noqa: E402
from stats import median  # noqa: E402

def main():
    outputs, counts, arm_of = load_outputs()
    syn = []
    for name in sorted(os.listdir(os.path.join(EXP, 'corpus'))):
        if name.startswith('synthetic_texts_months_') and name.endswith('.json'): syn += json.load(open(os.path.join(EXP, 'corpus', name), encoding='utf-8'))['texts']
    gt = {t['id']: t for t in syn}
    res = {}
    # 4.4 null precision
    FLAGS = {'narrative.meaning': 'meaning_stated', 'narrative.self_position': 'self_position_stated', 'emotion.bodily_sensation': 'bodily_sensation_stated',
             'emotion.appraisal.attribution': 'attribution_stated', 'salience.function': 'function_stated', 'narrative.turning_point': 'turning_point_stated'}
    npz = {}
    for unit, flag in FLAGS.items():
        npz[unit] = {}
        for m in EXTRACTORS:
            no_n = no_null = yes_n = yes_pop = 0
            for tid, t in gt.items():
                for rep, flat in outputs[m].get(tid, {}).items():
                    if flat is None: continue
                    v = get_unit(flat, unit)
                    populated = (v is True) if unit == 'narrative.turning_point' else (norm_text(v) is not None if not isinstance(v, bool) else v is not None)
                    if t[flag]: yes_n += 1; yes_pop += populated
                    else: no_n += 1; no_null += (not populated)
            npz[unit][m] = {'null_rate_on_no_texts': no_null / no_n if no_n else None, 'populated_rate_on_yes_texts': yes_pop / yes_n if yes_n else None, 'n_no': no_n, 'n_yes': yes_n}
    res['null_precision'] = npz
    # kind / arousal null rates (no ground truth)
    res['null_rate_no_gt'] = {u: {m: (lambda vals: sum(1 for v in vals if v == 'null') / len(vals) if vals else None)([norm_label(get_unit(f, u), u, None) for tid in gt for f in outputs[m].get(tid, {}).values() if f is not None]) for m in EXTRACTORS} for u in ('emotion.kind', 'emotion.arousal.text')}
    # 4.5 event_category accuracy
    acc = {}
    for m in EXTRACTORS:
        n = ok = 0
        for tid, t in gt.items():
            for flat in outputs[m].get(tid, {}).values():
                if flat is None: continue
                n += 1; ok += norm_label(get_unit(flat, 'context.event_category'), 'context.event_category', 'event_category') == t['category']
        acc[m] = ok / n if n else None
    res['event_category_accuracy_synthetic'] = acc
    # dimension value distributions per extractor (pooled 150 texts)
    dist = {}
    for u in ('emotion.intensity.value', 'salience.linkage_strength', 'emotion.valence.value', 'emotion.arousal.value', 'emotion.appraisal.urgency.value', 'emotion.appraisal.control.value'):
        dist[u] = {}
        for m in EXTRACTORS:
            vals = [num(get_unit(f, u)) for tid in outputs[m] for f in outputs[m][tid].values() if f is not None]
            nn = [v for v in vals if v is not None]
            c = collections.Counter(round(v, 2) for v in nn)
            dist[u][m] = {'n': len(vals), 'null_rate': 1 - len(nn) / len(vals) if vals else None, 'min': min(nn) if nn else None, 'median': median(nn) if nn else None, 'max': max(nn) if nn else None,
                          'distinct_values': len(c), 'top3': c.most_common(3)}
    res['dimension_values'] = dist
    # trait-language leakage: attachment / regulation words anywhere in the output of the 8 trait texts vs the 42 others
    WORDS = re.compile(r'\b(secure|anxious attachment|avoidant|disorganized|attachment|clingy|regulat(?:ed|ion)|dysregulat\w*|wavering)\b', re.I)
    leak = {}
    for m in EXTRACTORS:
        hit = {True: [0, 0], False: [0, 0]}
        for tid, t in gt.items():
            for flat in outputs[m].get(tid, {}).values():
                if flat is None: continue
                s = json.dumps({k: v for k, v in flat.items() if k != 'field_confidence'}, ensure_ascii=False)
                hit[t['trait_language']][1] += 1; hit[t['trait_language']][0] += bool(WORDS.search(s))
        leak[m] = {'trait_texts_rate': hit[True][0] / hit[True][1] if hit[True][1] else None, 'other_texts_rate': hit[False][0] / hit[False][1] if hit[False][1] else None}
    res['trait_language_leakage'] = leak
    # field_confidence summary
    fc = {}
    for m in EXTRACTORS:
        vals = []
        for tid in outputs[m]:
            for f in outputs[m][tid].values():
                if f and isinstance(f.get('field_confidence'), dict): vals += [num(x) for x in f['field_confidence'].values() if num(x) is not None]
        fc[m] = {'n': len(vals), 'median': median(vals) if vals else None, 'share_below_0.5': sum(1 for v in vals if v < 0.5) / len(vals) if vals else None}
    res['field_confidence'] = fc
    os.makedirs(SCORING, exist_ok=True)
    json.dump(res, open(os.path.join(SCORING, 'diagnostics.json'), 'w', encoding='utf-8'), indent=1, default=str)
    f = lambda x: '—' if x is None else f'{x:.2f}'
    L = ['# Diagnostics (generated by scripts/diagnostics.py)\n', '## Null precision, synthetic arm (§4.4; targets: null on "no" texts ≥ 0.95, populated on "yes" texts ≥ 0.80)\n',
         '| Field | ' + ' | '.join(f'{m} null-on-no / pop-on-yes' for m in EXTRACTORS) + ' |', '|---|' + '---|' * len(EXTRACTORS)]
    for u, d in npz.items(): L.append(f'| `{u}` | ' + ' | '.join(f"{f(d[m]['null_rate_on_no_texts'])} / {f(d[m]['populated_rate_on_yes_texts'])}" for m in EXTRACTORS) + ' |')
    L.append('\nNull rate on the synthetic arm for fields without a ground-truth flag: ' + '; '.join(f"`{u}`: " + ', '.join(f"{m} {f(v)}" for m, v in d.items()) for u, d in res['null_rate_no_gt'].items()))
    L.append('\n## `context.event_category` accuracy against the authored category (synthetic)\n\n' + ', '.join(f'{m} {f(v)}' for m, v in acc.items()))
    L.append('\n## Dimension values per extractor (pooled)\n\n| Unit | Extractor | n | null | min | median | max | distinct | top-3 values |\n|---|---|---|---|---|---|---|---|---|')
    for u, d in dist.items():
        for m, x in d.items(): L.append(f"| `{u}` | {m} | {x['n']} | {f(x['null_rate'])} | {f(x['min'])} | {f(x['median'])} | {f(x['max'])} | {x['distinct_values']} | {x['top3']} |")
    L.append('\n## Trait-language leakage (share of outputs containing attachment / regulation words)\n\n| Extractor | 8 trait-language texts | 42 other texts |\n|---|---|---|')
    for m, d in leak.items(): L.append(f"| {m} | {f(d['trait_texts_rate'])} | {f(d['other_texts_rate'])} |")
    L.append('\n## field_confidence\n\n| Extractor | values | median | share < 0.5 |\n|---|---|---|---|')
    for m, d in fc.items(): L.append(f"| {m} | {d['n']} | {f(d['median'])} | {f(d['share_below_0.5'])} |")
    open(os.path.join(SCORING, 'diagnostics.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
    print(open(os.path.join(SCORING, 'diagnostics.md'), encoding='utf-8').read())

if __name__ == '__main__':
    main()
