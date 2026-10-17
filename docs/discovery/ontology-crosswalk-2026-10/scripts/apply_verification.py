"""Apply a secondary-source verification pass to the research extractions in sources/group_*.json.

Usage:
  python -I scripts/apply_verification.py <sources-dir> <verification.json> [<verify_groupN.json> ...]

If per-group result files are given they are first consolidated into <verification.json> (committed, so the
pass is reproducible); otherwise <verification.json> is read as-is. Then, for every framework/construct in it:

  VERIFIED     -> construct.value_source = FETCHED, construct.verified_against = {...} (secondary verification)
  PARTIAL      -> value_source unchanged, verified_against recorded with status PARTIAL
  CONTRADICTED -> value_source unchanged, verified_against recorded with the source's version (values are NOT rewritten)
  UNVERIFIED   -> verified_against recorded with status UNVERIFIED

A framework whose source_status was KNOWLEDGE becomes FETCHED_SECONDARY when every one of its constructs that
carried a value list is VERIFIED; the verifying URLs are appended to fetched_urls and verification_notes.
Run merge_frameworks.py and crosswalk_build.py afterwards to regenerate frameworks.json and the matrix.
"""
import json, sys, glob, os

src_dir, ver_path, *group_files = sys.argv[1:]
ACCESSED = '2026-10-17'

if group_files:
    merged = {'generated': ACCESSED, 'purpose': 'Secondary-source verification of knowledge-reconstructed construct lists (REPORT.md section 9).',
              'method': 'For each construct, an accessible page showing the list was located (open-access paper/review, handbook chapter, university page, official site, Wikipedia last resort with its own citation recorded) and the list compared item by item. Quotes are from the fetched page text; PDFs without a text layer were extracted locally.',
              'frameworks': {}}
    for gf in group_files:
        d = json.load(open(gf, encoding='utf-8'))
        for fw, body in d['frameworks'].items():
            merged['frameworks'].setdefault(fw, {'constructs': {}})
            if body.get('best_source'): merged['frameworks'][fw]['best_source'] = body['best_source']
            merged['frameworks'][fw]['constructs'].update(body['constructs'])
    json.dump(merged, open(ver_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
ver = json.load(open(ver_path, encoding='utf-8'))

changes = []

# Resolve agent id <-> crosswalk id using merge_frameworks.py's table.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('mf', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'merge_frameworks.py'))
src = open(spec.origin, encoding='utf-8').read()
alias_src = src[src.index('ALIAS = {'):src.index('}\n', src.index('ALIAS = {')) + 1]
ns = {}; exec(alias_src, ns); AGENT_TO_CW = ns['ALIAS']; CW_TO_AGENT = {v: k for k, v in AGENT_TO_CW.items()}

def short(s, n=400):
    s = (s or '').strip().replace('\n', ' ')
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + ' ...'

for gf in sorted(glob.glob(os.path.join(src_dir, 'group_*.json'))):
    fws = json.load(open(gf, encoding='utf-8'))
    touched = False
    for fw in fws:
        cw = AGENT_TO_CW.get(fw['id'], fw['id'])
        v = ver['frameworks'].get(cw)
        if not v: continue
        urls = []
        for c in fw['constructs']:
            r = v['constructs'].get(c['id'])
            if not r: continue
            rec = {'status': r['status'], 'url': r.get('source_url'), 'title': r.get('source_title'), 'kind': r.get('source_kind'),
                   'accessed': r.get('accessed') or ACCESSED, 'quote': short(r.get('quote')), 'corrections': r.get('corrections') or 'none', 'note': short(r.get('note'), 600)}
            if r.get('wikipedia_citation'): rec['wikipedia_citation'] = r['wikipedia_citation']
            if r['status'] in ('CONTRADICTED', 'PARTIAL') and r.get('source_values'): rec['source_values'] = r['source_values']
            before = c.get('value_source')
            if r['status'] == 'VERIFIED' and c.get('value_source') == 'KNOWLEDGE':
                c['value_source'] = 'FETCHED'
            c['verified_against'] = rec
            c['verification_level'] = 'secondary'
            if r.get('source_url'): urls.append(r['source_url'])
            changes.append((cw, c['id'], before, c['value_source'], r['status'], r.get('source_kind')))
            touched = True
        if fw.get('source_status') == 'KNOWLEDGE':
            listed = [c for c in fw['constructs'] if c.get('values')]
            if listed and all(c.get('value_source') == 'FETCHED' for c in listed):
                fw['source_status'] = 'FETCHED_SECONDARY'
                fw['verification_notes'] = (fw.get('verification_notes') or '') + f' | {ACCESSED} verification pass: every construct list verified against an accessible secondary source (see constructs[].verified_against); status raised KNOWLEDGE -> FETCHED_SECONDARY. Confidence left as extracted.'
                changes.append((cw, '<framework>', 'KNOWLEDGE', 'FETCHED_SECONDARY', 'VERIFIED', v.get('best_source', {}).get('kind')))
        if urls:
            fw['fetched_urls'] = list(dict.fromkeys((fw.get('fetched_urls') or []) + urls))
    if touched:
        json.dump(fws, open(gf, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

print(f'{len(changes)} records updated')
for ch in changes: print('  ', ' | '.join(str(x) for x in ch))
