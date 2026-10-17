"""Crosswalk accuracy audit (ruling 2026-10-18, step 2).

Checks that draft-crosswalk/v0.8.3_to_v0.9.0.json accounts for every v0.8.3 affective field and every canonical value
with a disposition, that the v0.8.3 description / constraint text is preserved verbatim beside the v0.9 text, and that the
six core slots (core.anchor, spark, wound, fuel, bridge, echo) carry their 1-5 word constraints and examples verbatim.

The v0.8.3 source of truth is read from the published fragments (schema/fragments/{core,constellation,milky_way,gravity,impulse}.json),
not from fields.json, so the audit cannot inherit a mistake of the inventory.

Usage:
  python -I scripts/crosswalk_audit.py <repo-root> <crosswalk.json> <out.md> [--dump <findings.json>] [--before <findings.json>]

Exit code 1 when any v0.8.3 field or canonical value has no disposition (fail loudly); 0 otherwise, even with text discrepancies
(those are listed and must be fixed in the crosswalk, never in this audit).
"""
import json, os, re, sys

DOMAINS = ['core', 'constellation', 'milky_way', 'gravity', 'impulse']
CORE_SLOTS = ['core.anchor', 'core.spark', 'core.wound', 'core.fuel', 'core.bridge', 'core.echo']
FIELD_DISPOSITIONS = {'carried', 'renamed', 'reshaped', 'merged', 'cut-to-extensions', 'added', 'moved-to-trait'}
VALUE_DISPOSITIONS = {'carried', 'carried (deprecated)', 'cut-to-extensions', 'moved-to-trait', 'added'}
EXAMPLE_RE = re.compile(r'"([^"]+)"')


def load(p):
    return json.load(open(p, encoding='utf-8'))


def v083_source(repo):
    """fields and canonical values exactly as the published v0.8.3 fragments state them."""
    fields = {}
    for d in DOMAINS:
        frag = load(os.path.join(repo, 'schema', 'fragments', f'{d}.json'))
        for name, spec in frag['properties'].items():
            enum = [e for e in spec.get('enum', []) if e is not None] if 'enum' in spec else None
            canon = spec.get('x-edm-canonical')
            values = enum or canon or []
            fields[f'{d}.{name}'] = {
                'description': spec.get('description'),
                'constraints': spec.get('x_constraints'),
                'examples': EXAMPLE_RE.findall(spec.get('x_constraints') or '') if 'e.g.' in (spec.get('x_constraints') or '') else [],
                'values': list(values),
            }
    return fields


def audit(repo, cw):
    f = []  # findings: dict(kind, id, detail)
    src = v083_source(repo)
    n_values_src = sum(len(x['values']) for x in src.values())
    rows = {r['from']: r for r in cw.get('field_map', [])}

    # 1. every v0.8.3 field has a row with a disposition from the allowed set
    for path in src:
        r = rows.get(path)
        if r is None:
            f.append({'kind': 'FIELD_NO_DISPOSITION', 'id': path, 'detail': 'no field_map row'}); continue
        if r.get('disposition') not in FIELD_DISPOSITIONS:
            f.append({'kind': 'FIELD_NO_DISPOSITION', 'id': path, 'detail': f"disposition={r.get('disposition')!r}; allowed {sorted(FIELD_DISPOSITIONS)}"})
    for path in rows:
        if path not in src:
            f.append({'kind': 'FIELD_NOT_IN_V083', 'id': path, 'detail': 'field_map row has no v0.8.3 source field'})

    # 2. every canonical value has a disposition
    n_values_cw = 0
    for path, s in src.items():
        r = rows.get(path) or {}
        vals = {v['value']: v for v in (r.get('values') or [])}
        for v in s['values']:
            if v not in vals:
                f.append({'kind': 'VALUE_NO_DISPOSITION', 'id': f'{path} = {v}', 'detail': 'no value row'}); continue
            n_values_cw += 1
            if vals[v].get('disposition') not in VALUE_DISPOSITIONS:
                f.append({'kind': 'VALUE_NO_DISPOSITION', 'id': f'{path} = {v}', 'detail': f"disposition={vals[v].get('disposition')!r}"})
        for v in vals:
            if v not in s['values']:
                f.append({'kind': 'VALUE_NOT_IN_V083', 'id': f'{path} = {v}', 'detail': 'value row has no v0.8.3 source value'})

    # 3. v0.8.3 text preserved verbatim; v0.9 text present
    for path, s in src.items():
        r = rows.get(path)
        if r is None: continue
        old = r.get('v083') or {}
        if old.get('description') != s['description']:
            f.append({'kind': 'V083_DESCRIPTION', 'id': path, 'detail': f"crosswalk {old.get('description')!r} != fragment {s['description']!r}"})
        if (old.get('constraints') or None) != (s['constraints'] or None):
            f.append({'kind': 'V083_CONSTRAINTS', 'id': path, 'detail': f"crosswalk {old.get('constraints')!r} != fragment {s['constraints']!r}"})
        if r.get('disposition') != 'cut-to-extensions':
            new = r.get('v09') or {}
            if not new.get('description'):
                f.append({'kind': 'V09_DESCRIPTION_MISSING', 'id': path, 'detail': f"to={r.get('to')}"})

    # 4. six core slots: constraints and examples verbatim, in the Arm A block as well
    for path in CORE_SLOTS:
        s = src[path]; r = rows.get(path)
        if r is None: continue
        old = r.get('v083') or {}
        if old.get('examples') != s['examples']:
            f.append({'kind': 'CORE_SLOT_EXAMPLES', 'id': path, 'detail': f"crosswalk {old.get('examples')!r} != fragment {s['examples']!r}"})
        a = r.get('run2_arm_a')
        if not a:
            f.append({'kind': 'CORE_SLOT_ARM_A_MISSING', 'id': path, 'detail': 'no run2_arm_a block (v0.8.3 name, description, constraints, examples)'})
        else:
            for k, want in (('name', path.split('.')[1]), ('description', s['description']), ('constraints', s['constraints']), ('examples', s['examples'])):
                if a.get(k) != want:
                    f.append({'kind': 'CORE_SLOT_ARM_A', 'id': f'{path}.{k}', 'detail': f'{a.get(k)!r} != {want!r}'})

    # 5. new fields carry disposition "added"
    for n in cw.get('new_fields', []):
        if n.get('disposition') != 'added':
            f.append({'kind': 'NEW_FIELD_DISPOSITION', 'id': n.get('path'), 'detail': f"disposition={n.get('disposition')!r}"})

    # 6. summary arithmetic
    summ = cw.get('summary', {})
    if summ.get('affective_field_count_before') != len(src):
        f.append({'kind': 'SUMMARY', 'id': 'affective_field_count_before', 'detail': f"{summ.get('affective_field_count_before')} != {len(src)}"})
    if summ.get('canonical_values_before') != n_values_src:
        f.append({'kind': 'SUMMARY', 'id': 'canonical_values_before', 'detail': f"{summ.get('canonical_values_before')} != {n_values_src} (fragments)"})

    stats = {
        'fields_v083': len(src), 'values_v083': n_values_src, 'values_with_disposition': n_values_cw,
        'field_dispositions': _count(rows.values(), 'disposition'),
        'value_dispositions': _count((v for r in rows.values() for v in (r.get('values') or [])), 'disposition'),
        'new_fields': len(cw.get('new_fields', [])),
    }
    return f, stats


def _count(items, key):
    c = {}
    for it in items:
        c[it.get(key)] = c.get(it.get(key), 0) + 1
    return {str(k): v for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))}


def fatal(findings):
    return [x for x in findings if x['kind'] in ('FIELD_NO_DISPOSITION', 'VALUE_NO_DISPOSITION')]


def table(findings):
    if not findings: return '_none_\n'
    out = ['| # | Kind | Item | Detail |', '|---|---|---|---|']
    for i, x in enumerate(findings, 1):
        out.append(f"| {i} | `{x['kind']}` | `{x['id']}` | {x['detail'].replace('|', '\\|')} |")
    return '\n'.join(out) + '\n'


def summarise(findings):
    c = _count(findings, 'kind')
    return ', '.join(f'{k} × {v}' for k, v in c.items()) or 'none'


def main():
    args = sys.argv[1:]
    repo, cw_path, out_md = args[:3]
    dump = args[args.index('--dump') + 1] if '--dump' in args else None
    before = args[args.index('--before') + 1] if '--before' in args else None
    cw = load(cw_path)
    findings, stats = audit(repo, cw)
    if dump:
        json.dump({'crosswalk': cw_path, 'findings': findings, 'stats': stats}, open(dump, 'w', encoding='utf-8'), indent=1)
    fat = fatal(findings)
    lines = ['# Crosswalk audit — v0.8.3 → v0.9.0 draft (2026-10-18)', '',
             'Generated by `scripts/crosswalk_audit.py` (ruling 2026-10-18, step 2) against `draft-crosswalk/v0.8.3_to_v0.9.0.json`. '
             'Source of truth for v0.8.3: `schema/fragments/{core,constellation,milky_way,gravity,impulse}.json` (read directly, not via `fields.json`). '
             'Rule: discrepancies are fixed in the crosswalk generator (`scripts/v09_layout.py`), never in this audit.', '']
    if fat:
        lines += [f'## FAIL — {len(fat)} v0.8.3 field(s) or value(s) have no disposition', '']
    else:
        lines += ['## Result: every v0.8.3 field and canonical value has a disposition', '']
    lines += ['| Measure | Count |', '|---|---|',
              f"| v0.8.3 affective fields (fragments) | {stats['fields_v083']} |",
              f"| v0.8.3 canonical values (fragments; enum + x-edm-canonical, null excluded, booleans excluded) | {stats['values_v083']} |",
              f"| values with a disposition in the crosswalk | {stats['values_with_disposition']} |",
              f"| field dispositions | {', '.join(f'{k} {v}' for k, v in stats['field_dispositions'].items())} |",
              f"| value dispositions | {', '.join(f'{k} {v}' for k, v in stats['value_dispositions'].items())} |",
              f"| new v0.9 fields (disposition added) | {stats['new_fields']} |", '']
    if before:
        b = load(before)
        lines += [f"## Discrepancies found before the fix ({len(b['findings'])}; crosswalk as committed before this audit)", '',
                  f"Kinds: {summarise(b['findings'])}.", '', table(b['findings'])]
    lines += [f'## Discrepancies in the current crosswalk ({len(findings)})', '', f'Kinds: {summarise(findings)}.', '', table(findings)]
    lines += ['## What the audit checks', '',
              '1. Every affective field of the five v0.8.3 fragments has a `field_map` row whose `disposition` is one of carried / renamed / reshaped / merged / cut-to-extensions / added / moved-to-trait (moved-to-trait is the seventh disposition, outside the six named in the ruling; it covers `impulse.attachment_style` and `impulse.regulation_state`, which are neither cut nor carried into a canonical profile).',
              '2. Every canonical value (enum or `x-edm-canonical`) of those fields has a `values[]` row with a disposition (carried / carried (deprecated) / cut-to-extensions / moved-to-trait); no value row exists without a v0.8.3 source.',
              '3. `v083.description` and `v083.constraints` equal the fragment text verbatim; a `v09.description` exists for every row that is not cut.',
              '4. For the six core slots, `v083.examples` equals the quoted examples in the fragment constraint, and the `run2_arm_a` block (v0.8.3 name, description, constraints, examples) equals the fragment verbatim.',
              '5. Every `new_fields[]` entry carries disposition `added`.',
              '6. `summary.affective_field_count_before` and `summary.canonical_values_before` equal the fragment counts.', '']
    with open(out_md, 'w', encoding='utf-8', newline='\n') as fh: fh.write('\n'.join(lines))
    print(f"audit: {len(findings)} discrepancies ({summarise(findings)}); fatal {len(fat)}; stats {json.dumps(stats)}")
    sys.exit(1 if fat else 0)


if __name__ == '__main__':
    main()
