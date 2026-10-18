"""Re-embed run 3 into the v0.9 draft generator: rewrites the `RUN3` literal (section 3d) of
docs/discovery/ontology-crosswalk-2026-10/scripts/v09_layout.py from scoring/field_table.json (scripts/score.py), so the
draft schema build still reads no experiment file. Per lead unit: holds under reading (a) (frozen verdict) and (b) (R18),
`of` (3 voters + the new arms run: 8, or 9 once the R30 extension is scored), majority texts and null share, texts the
judge has not reached, the framing bound (kappa / ICC / judge same-class rate) and, per new arm, repeat / agree /
coverage under (a) and (b) / decision under (a) and (b) / borderline. The `ruling` string per unit is kept from the
existing literal; a unit whose string names R20 and whose judge is now complete gets the closing note.

Usage: python -P experiments/2026-10-18-run3/scripts/embed_run3.py [--check]   (--check: print the literal, write nothing)
"""
import json, os, re, sys, pprint
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(EXP))
LAYOUT = os.path.join(ROOT, 'docs', 'discovery', 'ontology-crosswalk-2026-10', 'scripts', 'v09_layout.py')
SHORT = {'google/gemini-4-argon': 'gemini-4-argon', 'qwen/qwen3.8-2.4t-a95b': 'qwen3.8-2.4t', 'meta-llama/llama-4-maverick': 'llama-4-maverick',
         'mistralai/mistral-large-4-0': 'mistral-large-4', 'openai/gpt-oss-120b': 'gpt-oss-120b', 'deepseek/deepseek-v4-pro-0813': 'deepseek-v4-pro'}


def r2(x): return None if x is None else round(float(x), 2)


def main():
    check = '--check' in sys.argv
    FT = json.load(open(os.path.join(EXP, 'scoring', 'field_table.json'), encoding='utf-8'))
    P = FT['table']['pooled']; units = [u for u, s, v in FT['units']]; new_arms = FT['new_arms']
    src = open(LAYOUT, encoding='utf-8').read()
    m = re.search(r'^RUN3 = \{\n(.*?)^\}\n', src, re.S | re.M)
    if not m: raise SystemExit('RUN3 literal not found in v09_layout.py')
    ns = {}; exec('RUN3 = {\n' + m.group(1) + '}\n', ns); old = ns['RUN3']
    lit = {}
    for u in units:
        r = P[u]; vd = r['verdict']; va = r['verdict_alt']; mj = r['majority']; fr = r['framing']
        fb = fr.get('kappa', fr.get('icc', fr.get('rate')))
        ruling = (old.get(u) or {}).get('ruling', 'held under both readings; not re-ruled (R18-R28 addendum)')
        twj = mj.get('texts_without_judge', 0) or 0
        if u == 'narrative.summary' and twj == 0 and 'closed' not in ruling: ruling = 'R20 (closed on the completed judge, 2026-10-18)'
        arms = {}
        for a in new_arms:
            x = r['arms'].get(a)
            if not x or not x.get('n_valid_outputs'): continue
            arms[SHORT[a]] = {'repeat': r2(x.get('repeat')), 'agree': r2(x.get('agree')), 'coverage_a': r2(x.get('coverage')), 'coverage_b': r2(x.get('coverage_valid')),
                              'a': x.get('decision'), 'b': x.get('decision_alt'), 'borderline': bool(x.get('borderline'))}
        lit[u] = {'holds_a': vd['total_hold'], 'holds_b': va['total_hold'], 'of': vd['total_hold_of'], 'majority_texts': mj.get('texts_with_majority'), 'majority_null_share': r2(mj.get('null_share_of_majority')),
                  'texts_without_judge': twj, 'framing_bound': r2(fb), 'ruling': ruling, 'arms': arms}
    # literal text in the existing layout (one unit per block; arms one per line)
    L = ['RUN3 = {']
    for u, d in lit.items():
        head = {k: d[k] for k in ('holds_a', 'holds_b', 'of', 'majority_texts', 'majority_null_share', 'texts_without_judge', 'framing_bound', 'ruling')}
        L.append(f" {u!r}: {{" + ', '.join(f'{k!r}: {v!r}' for k, v in head.items()) + ',')
        L.append("    'arms': {")
        items = list(d['arms'].items())
        for i, (a, x) in enumerate(items):
            L.append(f"             {a!r}: {{" + ', '.join(f'{k!r}: {v!r}' for k, v in x.items()) + '}' + (',' if i < len(items) - 1 else ''))
        L.append('    }},')
    L.append('}')
    new_lit = '\n'.join(L) + '\n'
    n_of = sorted({d['of'] for d in lit.values()}); n_new = len({a for d in lit.values() for a in d['arms']})
    rule = f"5-of-{n_of[0]} rule" + (' (R30 extension scored: DeepSeek V4 Pro the ninth model)' if 9 in n_of else ' after lever 3')
    src2 = src[:m.start()] + new_lit + src[m.end():]
    src2 = re.sub(r"^RUN3_SOURCE = '.*?'$", lambda _: "RUN3_SOURCE = " + repr(f"experiments/2026-10-18-run3/RESULTS.md sections 1-2 (pooled, 150 texts, {rule}, thresholds frozen in experiment-plan-run3.md section 7 at 974408e; R18 reading (b) decides, reading (a) frozen beside)"), src2, count=1, flags=re.M)
    src2 = re.sub(r"^RUN3_RULE_MIN = 5  # .*$", lambda _: f"RUN3_RULE_MIN = 5  # a field holds across the market when >= 5 of the {n_of[0]} models hold it (three voters by their classing run + >= 2 of the {n_new} new arms)", src2, count=1, flags=re.M)
    changed = {u: (old.get(u, {}).get('holds_a'), old.get(u, {}).get('holds_b'), old.get(u, {}).get('texts_without_judge')) for u in lit if (old.get(u, {}).get('holds_a'), old.get(u, {}).get('holds_b'), old.get(u, {}).get('of'), old.get(u, {}).get('texts_without_judge')) != (lit[u]['holds_a'], lit[u]['holds_b'], lit[u]['of'], lit[u]['texts_without_judge'])}
    print('units whose (holds_a, holds_b, of, texts_without_judge) changed (old values):', changed)
    print('new:', {u: (lit[u]['holds_a'], lit[u]['holds_b'], lit[u]['of'], lit[u]['texts_without_judge']) for u in changed})
    if check: print(new_lit); return 0
    open(LAYOUT, 'w', encoding='utf-8', newline='\n').write(src2); print('v09_layout.py RUN3 rewritten;', len(lit), 'units;', n_new, 'new arms; of =', n_of)
    return 0


if __name__ == '__main__':
    sys.exit(main())
