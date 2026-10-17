"""Build crosswalk.csv, crosswalk.md and crosswalk_stats.json from fields.json + crosswalk_data + decisions_data + frameworks.json."""
import json, csv, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crosswalk_data import FRAMEWORKS, FIELD_MAPS, VALUE_MAPS
from decisions_data import ORPHAN_DECISIONS, WEAK_FIELD_DECISIONS, GAPS, UNIQUE_EDM_RANKING

fields_path, frameworks_path, out_dir = sys.argv[1:4]
fields = json.load(open(fields_path, encoding='utf-8'))['fields']
fw_doc = json.load(open(frameworks_path, encoding='utf-8')) if os.path.exists(frameworks_path) else {'frameworks': []}
FW_IDS = [f[0] for f in FRAMEWORKS]; FW_NAME = {f[0]: f[2] for f in FRAMEWORKS}; FW_FAM = {f[0]: f[1] for f in FRAMEWORKS}
RELS = ['exact', 'broader', 'narrower', 'related']

# ---- verification index: framework -> list of (normalised value, source flag) ----
index = {}
for fw in fw_doc['frameworks']:
    items = []
    for c in fw.get('constructs', []):
        flag = 'V' if c.get('value_source') == 'FETCHED' else 'K'
        for v in (c.get('values') or []):
            items.append((str(v).lower(), flag))
        items.append((str(c.get('label', '')).lower(), flag)); items.append((c['id'].replace('_', ' ').lower(), flag))
    index[fw['id']] = items

def verify(fw, target):
    """Return V (found in fetched values), K (found only in knowledge values), '-' (not found / free-form)."""
    items = index.get(fw)
    if not items: return '?'
    best = '-'
    for piece in re.split(r'[;/]', re.sub(r'\(.*?\)', '', target)):
        p = piece.strip().lower()
        p = re.sub(r'\(.*?\)', '', p).strip()
        p = p.split(':')[0].strip() if p.startswith('mfoem') is False and re.match(r'^[a-z ]+:', p) else p
        if '#' in p: p = p.split('#')[-1]
        if p.startswith('mfoem:'): p = p.split()[0]
        p = re.sub(r'\s*\[.*?\]', '', p)
        p = p.replace('<', '').replace('>', '').replace('"', '').strip()
        if len(p) < 3: continue
        for v, flag in items:
            if p == v or re.search(r'(^|[^a-z])' + re.escape(p) + r'($|[^a-z])', v):
                if flag == 'V': return 'V'
                best = 'K'
    return best

# ---- rows ----
rows = []
field_by_path = {f['path']: f for f in fields}
for f in fields:
    rows.append({'id': f['path'], 'domain': f['domain'], 'field': f['field'], 'value': '', 'row_type': 'field', 'vocabulary': f['vocabulary'],
                 'description': f['description'] or '', 'maps': FIELD_MAPS.get(f['path'], [])})
    if f['vocabulary'] in ('closed_enum', 'canonical_open'):
        vm = VALUE_MAPS.get(f['path'], {})
        for v in f['canonical_values']:
            rows.append({'id': f"{f['path']}={v}", 'domain': f['domain'], 'field': f['field'], 'value': v, 'row_type': 'value', 'vocabulary': f['vocabulary'],
                         'description': '', 'maps': vm.get(v, [])})
# sanity: value maps for values that do not exist
for fp, vm in VALUE_MAPS.items():
    for v in vm:
        if v not in (field_by_path[fp]['canonical_values'] or []): raise SystemExit(f'unknown value {fp}={v}')
for fp in FIELD_MAPS:
    if fp not in field_by_path: raise SystemExit(f'unknown field {fp}')

def grounding(maps):
    rels = [m[1] for m in maps]
    if not rels: return 'orphan'
    if 'exact' in rels: return 'strong'
    if 'broader' in rels or 'narrower' in rels: return 'moderate'
    return 'weak'

for r in rows:
    for m in r['maps']:
        if m[0] not in FW_IDS: raise SystemExit(f'unknown framework {m[0]} in {r["id"]}')
        if m[1] not in RELS: raise SystemExit(f'bad relation {m}')
    r['grounding'] = grounding(r['maps'])
    r['counts'] = {rel: sum(1 for m in r['maps'] if m[1] == rel) for rel in RELS}
    r['counts']['none'] = len(FW_IDS) - len({m[0] for m in r['maps']})
    r['verified'] = [verify(m[0], m[2]) for m in r['maps']]

# ---- CSV ----
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, 'crosswalk.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['row_id', 'domain', 'field', 'value', 'row_type', 'vocabulary', 'grounding', 'n_exact', 'n_broader', 'n_narrower', 'n_related', 'n_none', 'targets_verified_V/K/-'] + FW_IDS)
    for r in rows:
        cells = {}
        for m, vflag in zip(r['maps'], r['verified']):
            cell = f"{m[1]}: {m[2]} [{vflag}]" + (f" ({m[3]})" if m[3] else '')
            cells[m[0]] = (cells[m[0]] + ' || ' + cell) if m[0] in cells else cell
        vsum = f"{r['verified'].count('V')}/{r['verified'].count('K')}/{r['verified'].count('-') + r['verified'].count('?')}"
        w.writerow([r['id'], r['domain'], r['field'], r['value'], r['row_type'], r['vocabulary'], r['grounding'],
                    r['counts']['exact'], r['counts']['broader'], r['counts']['narrower'], r['counts']['related'], r['counts']['none'], vsum]
                   + [cells.get(fw, 'none') for fw in FW_IDS])

# ---- stats ----
def pct(a, b): return round(100.0 * a / b, 1) if b else 0.0
frows = [r for r in rows if r['row_type'] == 'field']; vrows = [r for r in rows if r['row_type'] == 'value']
aff_frows = [r for r in frows if field_by_path[r['id']]['edm_kind'] != 'administrative']
stats = {
 'rows': len(rows), 'field_rows': len(frows), 'value_rows': len(vrows), 'frameworks': len(FW_IDS),
 'mappings_total': sum(len(r['maps']) for r in rows),
 'verification': {k: sum(r['verified'].count(k) for r in rows) for k in ['V', 'K', '-', '?']},
 'fields_by_grounding': {g: sum(1 for r in frows if r['grounding'] == g) for g in ['strong', 'moderate', 'weak', 'orphan']},
 'affective_fields_by_grounding': {g: sum(1 for r in aff_frows if r['grounding'] == g) for g in ['strong', 'moderate', 'weak', 'orphan']},
 'values_by_grounding': {g: sum(1 for r in vrows if r['grounding'] == g) for g in ['strong', 'moderate', 'weak', 'orphan']},
 'pct_fields_grounded_any': pct(sum(1 for r in frows if r['grounding'] != 'orphan'), len(frows)),
 'pct_fields_grounded_exact': pct(sum(1 for r in frows if r['grounding'] == 'strong'), len(frows)),
 'pct_values_grounded_any': pct(sum(1 for r in vrows if r['grounding'] != 'orphan'), len(vrows)),
 'pct_values_grounded_exact': pct(sum(1 for r in vrows if r['grounding'] == 'strong'), len(vrows)),
 'by_domain': {},
 'framework_coverage': {fw: {'rows_touched': sum(1 for r in rows if any(m[0] == fw for m in r['maps'])), 'exact': sum(1 for r in rows for m in r['maps'] if m[0] == fw and m[1] == 'exact')} for fw in FW_IDS},
 'orphans': [r['id'] for r in rows if r['grounding'] == 'orphan'],
 'weak_fields': [r['id'] for r in frows if r['grounding'] == 'weak'],
 'strong_fields': [r['id'] for r in frows if r['grounding'] == 'strong'],
}
for d in ['core', 'constellation', 'milky_way', 'gravity', 'impulse']:
    dr = [r for r in frows if r['domain'] == d]; dv = [r for r in vrows if r['domain'] == d]
    stats['by_domain'][d] = {'fields': len(dr), 'fields_strong': sum(1 for r in dr if r['grounding'] == 'strong'), 'fields_weak': sum(1 for r in dr if r['grounding'] == 'weak'), 'fields_orphan': sum(1 for r in dr if r['grounding'] == 'orphan'),
                             'values': len(dv), 'values_strong': sum(1 for r in dv if r['grounding'] == 'strong'), 'values_orphan': sum(1 for r in dv if r['grounding'] == 'orphan')}
json.dump(stats, open(os.path.join(out_dir, 'crosswalk_stats.json'), 'w', encoding='utf-8'), indent=1)

# ---- Markdown ----
L = []
L.append('# EDM v0.8.3 ontology crosswalk\n')
L.append('Generated 2026-10-17 from `fields.json` (57 fields, 185 canonical values) against 39 framework columns. Discovery output only; nothing normative.\n')
L.append('## Legend\n')
L.append('Relation direction is EDM -> target.\n')
L.append('| Relation | Meaning |\n|---|---|\n| exact | same concept (label may differ) |\n| broader | target is broader than the EDM concept |\n| narrower | target is narrower than the EDM concept |\n| related | overlapping or associated; neither subsumes the other |\n| none | no mapping (cells omitted from the tables below; full matrix in `crosswalk.csv`) |\n')
L.append('Verification flag on each target: **V** = target label found in a value list fetched from the framework\'s source; **K** = found only in a list reconstructed from model knowledge ([KNOWLEDGE]); **-** = free-form target (structural description, element name or paraphrase) not checkable against a value list. See `frameworks.json` for per-construct `value_source`.\n')
L.append('Grounding per row: **strong** = at least one exact mapping; **moderate** = broader/narrower only; **weak** = related only; **orphan** = no mapping.\n')
L.append('## Summary\n')
L.append(f"| Measure | Count |\n|---|---|\n| Field rows | {stats['field_rows']} |\n| Value rows | {stats['value_rows']} |\n| Mappings | {stats['mappings_total']} |\n| Targets verified V / K / - | {stats['verification']['V']} / {stats['verification']['K']} / {stats['verification']['-'] + stats['verification']['?']} |\n| Fields strong / moderate / weak / orphan | {stats['fields_by_grounding']['strong']} / {stats['fields_by_grounding']['moderate']} / {stats['fields_by_grounding']['weak']} / {stats['fields_by_grounding']['orphan']} |\n| Values strong / moderate / weak / orphan | {stats['values_by_grounding']['strong']} / {stats['values_by_grounding']['moderate']} / {stats['values_by_grounding']['weak']} / {stats['values_by_grounding']['orphan']} |\n")
L.append('| Domain | Fields | strong | weak | orphan | Values | strong | orphan |\n|---|---|---|---|---|---|---|---|')
for d, s in stats['by_domain'].items():
    L.append(f"| {d} | {s['fields']} | {s['fields_strong']} | {s['fields_weak']} | {s['fields_orphan']} | {s['values']} | {s['values_strong']} | {s['values_orphan']} |")
L.append('\n### Framework coverage (rows touched / exact mappings)\n')
L.append('| Framework | Family | Rows touched | Exact |\n|---|---|---|---|')
for fw in FW_IDS:
    c = stats['framework_coverage'][fw]; L.append(f"| {FW_NAME[fw]} | {FW_FAM[fw]} | {c['rows_touched']} | {c['exact']} |")
L.append('\n## Matrix by domain\n')
cur_domain = None; cur_field = None
for r in rows:
    if r['domain'] != cur_domain:
        cur_domain = r['domain']; L.append(f"\n## {cur_domain.upper()}\n")
    if r['row_type'] == 'field':
        cur_field = r['field']
        L.append(f"\n### `{r['id']}` — {r['vocabulary']} — grounding: **{r['grounding']}**\n")
        if r['description']: L.append(f"_{r['description']}_\n")
        if r['maps']:
            L.append('| Framework | Relation | Target | Ver. | Note |\n|---|---|---|---|---|')
            for m, vf in zip(r['maps'], r['verified']): L.append(f"| {FW_NAME[m[0]]} | {m[1]} | {m[2]} | {vf} | {m[3]} |")
        else:
            L.append('_No framework mapping (orphan)._')
    else:
        L.append(f"\n**`{r['value']}`** — grounding: {r['grounding']}\n")
        if r['maps']:
            L.append('| Framework | Relation | Target | Ver. | Note |\n|---|---|---|---|---|')
            for m, vf in zip(r['maps'], r['verified']): L.append(f"| {FW_NAME[m[0]]} | {m[1]} | {m[2]} | {vf} | {m[3]} |")
        else:
            L.append('_orphan_')

# ---- Gap list a: orphans ----
L.append('\n\n## Gap list A — Orphans (EDM rows with no mapping anywhere)\n')
L.append('| Row | Decision | Reason |\n|---|---|---|')
missing = []
for r in rows:
    if r['grounding'] == 'orphan':
        d = ORPHAN_DECISIONS.get(r['id'])
        if d is None: missing.append(r['id']); d = ('UNDECIDED', '')
        L.append(f"| `{r['id']}` | {d[0]} | {d[1]} |")
if missing: print('WARNING orphan rows without decision:', missing)
L.append('\n### A2 — Weakly grounded fields (related-only) and duplicate fields: decisions\n')
L.append('| Field | Grounding | Decision | Reason |\n|---|---|---|---|')
for r in frows:
    if r['id'] in WEAK_FIELD_DECISIONS:
        d = WEAK_FIELD_DECISIONS[r['id']]; L.append(f"| `{r['id']}` | {r['grounding']} | {d[0]} | {d[1]} |")
undec = [r['id'] for r in frows if r['grounding'] == 'weak' and r['id'] not in WEAK_FIELD_DECISIONS]
if undec: print('WARNING weak fields without decision:', undec)

# ---- Gap list b ----
L.append('\n## Gap list B — Framework constructs with no EDM home\n')
L.append('| Framework(s) | Construct | Decision | Reason / target |\n|---|---|---|---|')
for g in GAPS: L.append(f"| {g[0]} | {g[1]} | {g[2]} | {g[3]} |")
gap_counts = {k: sum(1 for g in GAPS if g[2] == k) for k in ['add', 'covered', 'out_of_scope']}
stats['gap_decisions'] = gap_counts
stats['orphan_decisions'] = {k: sum(1 for v in ORPHAN_DECISIONS.values() if v[0] == k) for k in ['keep', 'cut', 'merge']}
stats['weak_field_decisions'] = {k: sum(1 for v in WEAK_FIELD_DECISIONS.values() if v[0] == k) for k in ['keep', 'cut', 'merge']}
json.dump(stats, open(os.path.join(out_dir, 'crosswalk_stats.json'), 'w', encoding='utf-8'), indent=1)
open(os.path.join(out_dir, 'crosswalk.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(json.dumps({k: stats[k] for k in ['rows', 'mappings_total', 'verification', 'fields_by_grounding', 'values_by_grounding', 'pct_fields_grounded_any', 'pct_fields_grounded_exact', 'pct_values_grounded_any', 'pct_values_grounded_exact', 'gap_decisions', 'orphan_decisions']}, indent=1))
print('orphans:', stats['orphans'])
print('weak fields:', stats['weak_fields'])
