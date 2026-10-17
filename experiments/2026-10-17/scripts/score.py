"""Scoring for the 2026-10-17 experiment (experiment-plan.md section 4): loads raw/<model>/<arm>.jsonl, normalises labels,
computes Fleiss kappa (coded units), judge-equivalence rates (free-text units, from raw/judge/*.jsonl) and ICC(2,1)
(dimension values), applies the frozen decision rule per arm and pooled, and writes scoring/field_table.{json,md}.

Usage: python -P experiments/2026-10-17/scripts/score.py
"""
import json, os, re, sys, math
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(EXP))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'docs', 'discovery', 'ontology-crosswalk-2026-10', 'scripts'))
from stats import fleiss_kappa, icc2_1, pairwise_same_rate, modal, median  # noqa: E402
import v09_layout as L  # noqa: E402

MODELS = json.load(open(os.path.join(EXP, 'models.json'), encoding='utf-8'))
EXTRACTORS = [e['model'] for e in MODELS['extractors'].values()]
RAW = os.path.join(EXP, 'raw'); SCORING = os.path.join(EXP, 'scoring')
ARMS = ('synthetic', 'conversational', 'pepys')
THRESH = {'C': (0.70, 0.40), 'CL': (0.70, 0.40), 'B': (0.70, 0.40), 'T': (0.80, 0.60), 'S': (0.80, 0.60), 'L': (0.80, 0.60), 'D': (0.75, 0.50), 'N': (0.75, 0.50)}

# scored units: (unit path, shape, vocabulary name for canonical check or None)
UNITS = []
def _u(p, s, v=None): UNITS.append((p, s, v))
for f in ('subject', 'trigger', 'harm', 'drive', 'integration', 'meaning', 'identity_link', 'valence_shift', 'self_position'): _u(f'narrative.{f}', 'T')
_u('narrative.summary', 'S'); _u('narrative.turning_point', 'B'); _u('narrative.arc', 'CL', 'arc')
_u('emotion.primary', 'C', 'emotion'); _u('emotion.secondary', 'CL', 'emotion'); _u('emotion.kind', 'C', 'kind')
for d, v in (('valence', 'valence'), ('arousal', 'arousal'), ('intensity', None), ('appraisal.urgency', 'urgency'), ('appraisal.control', 'control')):
    _u(f'emotion.{d}.text', 'C', v); _u(f'emotion.{d}.value', 'D')
_u('emotion.meta', 'T'); _u('emotion.bodily_sensation', 'T'); _u('emotion.temporal_profile', 'C', 'temporal_profile'); _u('emotion.appraisal.attribution', 'C', 'attribution')
_u('context.event', 'T'); _u('context.event_category', 'C', 'event_category'); _u('context.place', 'T'); _u('context.people', 'L')
_u('context.relationship', 'C', 'relationship'); _u('context.relationship_model', 'C', 'relationship_model'); _u('context.life_stage', 'C', 'life_stage')
_u('context.scope.text', 'C', 'scope'); _u('context.scope.direction', 'C')
_u('salience.memory_type', 'C', 'memory_type'); _u('salience.tether.type', 'C', 'tether'); _u('salience.tether.referent', 'T'); _u('salience.tether.stake', 'T')
_u('salience.retrieval_cues', 'L'); _u('salience.themes', 'L'); _u('salience.recurrence', 'C', 'recurrence')
_u('salience.persistence.text', 'C', 'persistence'); _u('salience.persistence.decay', 'C'); _u('salience.linkage_strength', 'N')
_u('salience.function', 'CL', 'function'); _u('salience.resilience', 'L'); _u('salience.trajectory', 'C', 'trajectory')
for f in ('action_tendency', 'need', 'temporal_focus', 'risk_posture', 'coping'): _u(f'motivation.{f}', 'C', f)
FREE_TEXT_UNITS = [p for p, s, v in UNITS if s in ('T', 'S', 'L')]
DEP = {}
for f, v, to, why in L.DEPRECATED_VALUES: DEP[(f, v)] = to or v
PERSISTENCE_RANK = {'transient': 0.25, 'short': 0.5, 'enduring': 0.75, 'chronic': 1.0}

def flatten(parsed):
    """accept the flat dotted form (expected) or a nested-domain form; return dict keyed by the 47 dotted paths."""
    if not isinstance(parsed, dict): return {}
    if any(k in parsed for k in L.ALL_09): return parsed
    out = {}
    for dom, fields in L.LAYOUT_ORDER.items():
        d = parsed.get(dom)
        if not isinstance(d, dict): continue
        for f in fields:
            if '.' in f:
                a, b = f.split('.'); v = (d.get(a) or {}).get(b) if isinstance(d.get(a), dict) else None
            else: v = d.get(f)
            out[f'{dom}.{f}'] = v
    return out

def get_unit(flat, unit):
    """raw value of a scored unit from a flattened output."""
    if unit in flat: return flat.get(unit)
    base, _, sub = unit.rpartition('.')
    if base in flat and isinstance(flat[base], dict): return flat[base].get(sub)
    return None

def norm_label(v, unit, vocab):
    if v is None: return 'null'
    if isinstance(v, bool): return 'true' if v else 'false'
    if isinstance(v, list):
        if not v: return 'null'
        v = v[0]
    if isinstance(v, dict): v = v.get('text')
    if v is None: return 'null'
    s = re.sub(r'\s+', ' ', str(v)).strip().lower()
    if s in ('', 'null', 'none', 'n/a'): return 'null'
    s = s.replace(' ', '_').replace('-', '_')
    field = {'arc': 'narrative.arc', 'relationship': 'context.relationship', 'memory_type': 'salience.memory_type', 'persistence': 'salience.persistence',
             'recurrence': 'salience.recurrence', 'trajectory': 'salience.trajectory', 'temporal_profile': 'emotion.temporal_profile'}.get(vocab)
    if field: s = DEP.get((field, s), s)
    return s

def norm_text(v):
    """free-text answer as shown to the judge; lists joined sorted."""
    if v is None: return None
    if isinstance(v, list):
        items = [norm_text(x) for x in v]; items = sorted(i for i in items if i)
        return '; '.join(items) if items else None
    if isinstance(v, dict): v = v.get('text')
    if v is None: return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return s if s and s.lower() not in ('null', 'none') else None

def num(v):
    if isinstance(v, bool) or v is None: return None
    if isinstance(v, (int, float)): return float(v) if not math.isnan(v) else None
    if isinstance(v, dict): return num(v.get('value'))
    try: return float(str(v).strip())
    except Exception: return None

def load_outputs(raw_dir=RAW, models=EXTRACTORS, arms=ARMS):
    """-> outputs[model][text_id][repeat] = flat dict (valid) | None (failed); meta counts."""
    outputs = {m: defaultdict(dict) for m in models}; counts = defaultdict(Counter); arm_of = {}
    for m in models:
        for arm in arms:
            p = os.path.join(raw_dir, m, f'{arm}.jsonl')
            if not os.path.exists(p): continue
            for line in open(p, encoding='utf-8'):
                if not line.strip(): continue
                r = json.loads(line); arm_of[r['text_id']] = arm
                ok = isinstance(r.get('parsed'), dict) and r.get('transport_error') is None
                outputs[m][r['text_id']][r['repeat']] = flatten(r['parsed']) if ok else None
                counts[m]['calls'] += 1; counts[m]['valid' if ok else 'invalid'] += 1
    return outputs, counts, arm_of

def load_judge():
    """raw/judge/*.jsonl -> groups[(text_id, unit)][answer_key] = group id (answer_key = 'model#repeat')."""
    groups = {}
    d = os.path.join(RAW, 'judge')
    if not os.path.isdir(d): return groups
    for f in sorted(os.listdir(d)):
        if not f.endswith('.jsonl'): continue
        for line in open(os.path.join(d, f), encoding='utf-8'):
            if not line.strip(): continue
            r = json.loads(line)
            if not r.get('groups'): continue
            for unit, g in r['groups'].items(): groups[(r['text_id'], unit)] = g
    return groups

def model_labels(outputs, m, tid, unit, shape, vocab):
    """normalised labels over valid repeats; numbers for D/N."""
    out = []
    for rep in sorted(outputs[m].get(tid, {})):
        flat = outputs[m][tid][rep]
        if flat is None: continue
        v = get_unit(flat, unit)
        out.append(num(v) if shape in ('D', 'N') else norm_label(v, unit, vocab))
    return out

def score_unit(outputs, texts, unit, shape, vocab, judge):
    lo_r, lo_x = THRESH[shape]
    res = {'unit': unit, 'shape': shape, 'repeat': {}, 'cross': None, 'null_rate': None, 'noncanonical_rate': None, 'notes': []}
    nulls = tot = noncan = nonnull = 0
    per_model_rep = {}
    cross_rows = []
    if shape in ('D', 'N'):
        for m in EXTRACTORS:
            rows = []
            for tid in texts:
                vals = model_labels(outputs, m, tid, unit, shape, vocab)
                tot += len(vals) + sum(1 for rep in outputs[m].get(tid, {}) if outputs[m][tid][rep] is not None) - len(vals)
                nums = [v for v in vals if v is not None]; nulls += len(vals) - len(nums)
                if len(nums) == 5: rows.append(nums)
            icc = icc2_1(rows) if len(rows) >= 2 else None
            per_model_rep[m] = {'icc': icc, 'texts_complete': len(rows), 'texts': len(texts)}
        # cross: per-model means where every model has >= 1 number
        for tid in texts:
            means = []
            for m in EXTRACTORS:
                nums = [v for v in model_labels(outputs, m, tid, unit, shape, vocab) if v is not None]
                means.append(sum(nums) / len(nums) if nums else None)
            if all(x is not None for x in means): cross_rows.append(means)
        res['cross'] = {'icc': icc2_1(cross_rows) if len(cross_rows) >= 2 else None, 'texts_complete': len(cross_rows)}
        stat_r = {m: per_model_rep[m]['icc'] for m in EXTRACTORS}; stat_x = res['cross']['icc']
    elif shape in ('T', 'S', 'L'):
        for m in EXTRACTORS:
            rates = []; nn_rates = []
            for tid in texts:
                g = judge.get((tid, unit))
                if g is None: continue
                labels = [g.get(f'{m}#{rep}') for rep in sorted(outputs[m].get(tid, {})) if outputs[m][tid][rep] is not None]
                labels = [l for l in labels if l is not None]
                r = pairwise_same_rate(labels)
                if r is not None: rates.append(r)
                nn = [l for l in labels if l != 'null']  # descriptive: agreement among populated answers only
                r2 = pairwise_same_rate(nn)
                if r2 is not None: nn_rates.append(r2)
            per_model_rep[m] = {'rate': sum(rates) / len(rates) if rates else None, 'texts': len(rates), 'rate_nonnull': sum(nn_rates) / len(nn_rates) if nn_rates else None, 'texts_nonnull': len(nn_rates)}
        xr = []
        for tid in texts:
            g = judge.get((tid, unit))
            if g is None: continue
            reps = []
            for m in EXTRACTORS:
                labels = [g.get(f'{m}#{rep}') for rep in sorted(outputs[m].get(tid, {})) if outputs[m][tid][rep] is not None]
                labels = [l for l in labels if l is not None]
                if labels: reps.append(modal(labels))
            r = pairwise_same_rate(reps)
            if r is not None: xr.append(r)
        xr_nn = []
        for tid in texts:
            g = judge.get((tid, unit))
            if g is None: continue
            reps = []
            for m in EXTRACTORS:
                labels = [g.get(f'{m}#{rep}') for rep in sorted(outputs[m].get(tid, {})) if outputs[m][tid][rep] is not None]
                labels = [l for l in labels if l is not None and l != 'null']
                if labels: reps.append(modal(labels))
            r = pairwise_same_rate(reps)
            if r is not None: xr_nn.append(r)
        res['cross'] = {'rate': sum(xr) / len(xr) if xr else None, 'texts': len(xr), 'rate_nonnull': sum(xr_nn) / len(xr_nn) if xr_nn else None, 'texts_nonnull': len(xr_nn)}
        for m in EXTRACTORS:
            for tid in texts:
                for rep, flat in outputs[m].get(tid, {}).items():
                    if flat is None: continue
                    tot += 1; nulls += norm_text(get_unit(flat, unit)) is None
        stat_r = {m: per_model_rep[m]['rate'] for m in EXTRACTORS}; stat_x = res['cross']['rate']
        if not judge: res['notes'].append('judge pending')
    else:
        canon = L.CANONICAL.get(vocab, set()) if vocab else None
        for m in EXTRACTORS:
            subj = []
            for tid in texts:
                labels = model_labels(outputs, m, tid, unit, shape, vocab)
                subj.append(labels)
                for l in labels:
                    tot += 1; nulls += l == 'null'
                    if canon is not None and l != 'null':
                        nonnull += 1; noncan += l not in canon
            k, info = fleiss_kappa(subj)
            per_model_rep[m] = {'kappa': k, 'perfect_degenerate': k is None and info.get('P_bar') == 1.0, 'subjects': info.get('subjects'), 'categories': info.get('categories')}
        for tid in texts:
            row = []
            for m in EXTRACTORS:
                labels = model_labels(outputs, m, tid, unit, shape, vocab)
                if labels: row.append(modal(labels))
            cross_rows.append(row)
        k, info = fleiss_kappa(cross_rows)
        res['cross'] = {'kappa': k, 'perfect_degenerate': k is None and info.get('P_bar') == 1.0, 'subjects': info.get('subjects'), 'categories': info.get('categories')}
        stat_r = {m: (1.0 if per_model_rep[m]['perfect_degenerate'] else per_model_rep[m]['kappa']) for m in EXTRACTORS}
        stat_x = 1.0 if res['cross']['perfect_degenerate'] else res['cross']['kappa']
        if nonnull: res['noncanonical_rate'] = noncan / nonnull
    res['repeat'] = per_model_rep
    res['null_rate'] = nulls / tot if tot else None
    # decision
    passes = [m for m in EXTRACTORS if stat_r.get(m) is not None and stat_r[m] >= lo_r]
    fails = [m for m in EXTRACTORS if stat_r.get(m) is not None and stat_r[m] < lo_r]
    pending = [m for m in EXTRACTORS if stat_r.get(m) is None]
    if len(pending) > 1 or stat_x is None: outcome = 'pending'
    elif len(fails) >= 2: outcome = 'cut'
    elif len(passes) >= 3 and stat_x >= lo_x: outcome = 'pass'
    elif len(passes) >= 3: outcome = 'interpretive'
    else: outcome = 'cut'  # exactly 2 pass + 1 pending/fail -> fails the >= 3 rule
    border = any(stat_r.get(m) is not None and abs(stat_r[m] - lo_r) < 0.05 for m in EXTRACTORS) or (stat_x is not None and abs(stat_x - lo_x) < 0.05)
    res.update({'stat_repeat': stat_r, 'stat_cross': stat_x, 'models_pass_repeat': passes, 'outcome': outcome, 'borderline': border,
                'sparse': res['null_rate'] is not None and res['null_rate'] >= 0.90})
    return res

def fmt(x): return '—' if x is None else f'{x:.2f}'

def main():
    outputs, counts, arm_of = load_outputs(); judge = load_judge()
    os.makedirs(SCORING, exist_ok=True)
    texts_by_arm = defaultdict(list)
    for tid, arm in arm_of.items(): texts_by_arm[arm].append(tid)
    for a in texts_by_arm: texts_by_arm[a].sort()
    all_texts = sorted(arm_of)
    table = {}
    for scope, texts in [('pooled', all_texts)] + [(a, texts_by_arm[a]) for a in ARMS if texts_by_arm[a]]:
        table[scope] = {unit: score_unit(outputs, texts, unit, shape, vocab, judge) for unit, shape, vocab in UNITS}
    json.dump({'counts': counts, 'texts_per_arm': {a: len(v) for a, v in texts_by_arm.items()}, 'table': table}, open(os.path.join(SCORING, 'field_table.json'), 'w', encoding='utf-8'), indent=1, default=str)
    lines = ['# Per-unit scoring (generated by scripts/score.py)\n', f"Outputs loaded: {json.dumps({m: dict(c) for m, c in counts.items()})}; texts per arm: {dict((a, len(v)) for a, v in texts_by_arm.items())}\n"]
    short = {m: m.replace('claude-', '').replace('gpt-', 'gpt') for m in EXTRACTORS}
    for scope in table:
        lines.append(f'\n## {scope}\n')
        lines.append('| Unit | Shape | ' + ' | '.join(f'rep {short[m]}' for m in EXTRACTORS) + ' | cross | null rate | non-canon | outcome | flags |')
        lines.append('|---|---|' + '---|' * len(EXTRACTORS) + '---|---|---|---|---|')
        for unit, shape, vocab in UNITS:
            r = table[scope][unit]
            flags = ', '.join(x for x, y in (('borderline', r['borderline']), ('sparse', r['sparse'])) if y) + (' ' + '; '.join(r['notes']) if r['notes'] else '')
            lines.append(f"| {unit} | {shape} | " + ' | '.join(fmt(r['stat_repeat'].get(m)) for m in EXTRACTORS) + f" | {fmt(r['stat_cross'])} | {fmt(r['null_rate'])} | {fmt(r['noncanonical_rate'])} | **{r['outcome']}** | {flags} |")
        c = Counter(table[scope][u]['outcome'] for u, s, v in UNITS)
        lines.append(f"\nOutcomes: {dict(c)}")
    open(os.path.join(SCORING, 'field_table.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    print('scored', len(UNITS), 'units;', {s: dict(Counter(table[s][u]['outcome'] for u, sh, v in UNITS)) for s in table})

if __name__ == '__main__':
    main()
