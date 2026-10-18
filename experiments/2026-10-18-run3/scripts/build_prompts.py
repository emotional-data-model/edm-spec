"""Run-3 prompts (experiment-plan-run3.md section 4): one shared system prompt for all eight extractors = the run-1 header
(experiments/2026-10-17/prompts/extraction_system.txt) with the three edits the plan states (profile name and field count,
rule 2 stated-only list without `meaning` (R6), rule 3 without `linkage_strength`), followed by a 19-field block generated
from the draft fragments (draft-schema/fragments/*.json: description, x_constraints, x_recommended_values) for the R17
comparable tier (`v09_layout.PROFILES_09['essential']`) in LAYOUT_ORDER. The block is cross-checked against
`v09_layout.DESC` (description and constraints must agree with the fragments) and the header against the run-1 file; a
mismatch aborts. Judge prompts = run-2 judge_system.txt (rules 1-5) and judge_user.txt verbatim. No API calls.

Usage: python -P experiments/2026-10-18-run3/scripts/build_prompts.py [--check]   (--check: compare, write nothing; exit 1 on drift)
"""
import json, os, sys, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP); ROOT = os.path.dirname(EXPS)
RUN1 = os.path.join(EXPS, '2026-10-17'); RUN2 = os.path.join(EXPS, '2026-10-18-run2')
DISC = os.path.join(ROOT, 'docs', 'discovery', 'ontology-crosswalk-2026-10'); DRAFT = os.path.join(DISC, 'draft-schema')
sys.path.insert(0, os.path.join(DISC, 'scripts'))
import v09_layout as L  # noqa: E402

FIELDS = list(L.PROFILES_09['essential'])
assert len(FIELDS) == 19, FIELDS
ORDERED = [f'{d}.{f}' for d, fs in L.LAYOUT_ORDER.items() for f in fs if f'{d}.{f}' in FIELDS]
assert sorted(ORDERED) == sorted(FIELDS)
FRAG = {d: json.load(open(os.path.join(DRAFT, 'fragments', f'{d}.json'), encoding='utf-8')) for d in L.LAYOUT_ORDER}
STATED_ONLY = ['self_position', 'bodily_sensation', 'appraisal.attribution', 'turning_point', 'function']  # plan section 4: not `meaning` (R6)


def node_of(path):
    dom, _, f = path.partition('.')
    node = FRAG[dom]['properties']
    if f.startswith('appraisal.'): return node['appraisal']['properties'][f.split('.')[1]]
    return node[f]


def shape_of(path, node):
    if path == 'context.scope': return '{"text": string|null, "direction": string|null}'
    if path == 'salience.tether': return '{"type": string|null, "referent": string|null, "stake": string|null}'
    if path == 'emotion.intensity': return '{"text": string|null, "value": number in [0, 1]|null}'
    t = node.get('type')
    if 'allOf' in node: return 'string|null  (the value word)'
    if t in (['array', 'null'], 'array'):
        return 'array of strings (value words)' if 'allOf' in node.get('items', {}) else 'array of strings'
    if t == ['boolean', 'null']: return 'true|false|null'
    return 'string|null'


def field_block():
    lines = []; dom_seen = None
    for path in ORDERED:
        dom = path.split('.')[0]
        if dom != dom_seen: lines.append(f'\n## {dom}'); dom_seen = dom
        node = node_of(path)
        desc = node.get('description', '').replace('\n', ' '); cons = node.get('x_constraints', '').replace('\n', ' ')
        d_desc, d_cons = L.DESC[path]
        if desc != d_desc.replace('\n', ' ') or cons != d_cons.replace('\n', ' '):
            raise SystemExit(f'draft-schema fragment and v09_layout.DESC differ on {path}; run aborted')
        rec = node.get('x_recommended_values'); extra = ''
        if path == 'context.scope':
            rec = node['properties']['text'].get('x_recommended_values'); extra = f"; direction one of {node['properties']['direction']['x_recommended_values']}"
        elif path == 'salience.tether':
            rec = node['properties']['type'].get('x_recommended_values'); extra = ' (applies to tether.type)'
        line = f'- `{path}` -> {shape_of(path, node)}\n    {desc}'
        if cons: line += f'\n    Constraints: {cons}'
        if rec: line += f'\n    Recommended values: {", ".join(rec)}{extra}. Other wording is accepted when none fits.'
        lines.append(line)
    return '\n'.join(lines)


def header():
    r1 = open(os.path.join(RUN1, 'prompts', 'extraction_system.txt'), encoding='utf-8').read()
    h = r1.split('\nFields (47)')[0]
    edits = [
        ('Full profile (47 affective fields)', 'Essential profile (19 affective fields; the R17 comparable tier)'),
        ('fill the 47 fields below', 'fill the 19 fields below'),
        ('(self_position, kind, arousal, appraisal.attribution, bodily_sensation, meaning, turning_point, function)', '(' + ', '.join(STATED_ONLY) + ')'),
        (" `salience.linkage_strength` is how strongly the text links this experience to other memories or themes (0 isolated to 1 central).", ''),
        ('e.g. "emotion.appraisal.urgency"', 'e.g. "emotion.appraisal.attribution"'),
    ]
    for a, b in edits:
        if a not in h: raise SystemExit(f'run-1 header lacks the expected text: {a[:60]}')
        h = h.replace(a, b)
    return h + '\nFields (19)'


def build():
    sys_prompt = header() + field_block() + '\n'
    user = open(os.path.join(RUN1, 'prompts', 'extraction_user.txt'), encoding='utf-8').read()
    judge_sys = open(os.path.join(RUN2, 'prompts', 'judge_system.txt'), encoding='utf-8').read()
    judge_usr = open(os.path.join(RUN2, 'prompts', 'judge_user.txt'), encoding='utf-8').read()
    assert '5. LENGTH IS NOT A DIFFERENCE' in judge_sys
    return {'extraction_system.txt': sys_prompt, 'extraction_user.txt': user, 'judge_system.txt': judge_sys, 'judge_user.txt': judge_usr}


def main():
    out = build(); pd = os.path.join(EXP, 'prompts'); os.makedirs(pd, exist_ok=True)
    check = '--check' in sys.argv; drift = False
    for n, t in out.items():
        p = os.path.join(pd, n)
        if check:
            cur = open(p, encoding='utf-8').read() if os.path.exists(p) else None
            ok = cur == t; drift |= not ok
            print(f'{n:<22} {"OK" if ok else "DRIFT"}')
        else:
            open(p, 'w', encoding='utf-8', newline='\n').write(t)
            print(f'{n:<22} {len(t):>6} chars sha256 {hashlib.sha256(t.encode()).hexdigest()[:16]}')
    if check and drift: sys.exit(1)
    if not check: print('19-field block agrees with draft-schema fragments and v09_layout.DESC; header derived from run-1 extraction_system.txt')


if __name__ == '__main__':
    main()
