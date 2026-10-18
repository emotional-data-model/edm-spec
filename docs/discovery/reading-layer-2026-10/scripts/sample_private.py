"""Private-arm sampler for run 4 (experiment-plan-run4.md section 9.1). WRITTEN, NOT RUN. Deferred until the conditions in
section 9 hold (Anthropic direct access restored, no gateway, founder present).

Walks an archive root (any tree of .txt, .md or .json files; a .json file contributes its "text" / "content" / "body"
string field), reads each file ONLY to compute sha256, code-point length and a year (YAML front matter `date:`, else a
leading ISO date in the file name, else the file's modification time), stratifies by year x length tercile, draws N
with the founder's seed, and writes a manifest (id = sha256[:12], relative path, sha256, length, year, tercile) to a path
OUTSIDE the repository. It never prints, copies or stores text. --dry-run lists the strata counts only.

Usage: python -I docs/discovery/reading-layer-2026-10/scripts/sample_private.py <archive-root> --seed <founder's seed> --out <path outside edm-spec> [--n 50] [--dry-run]
"""
import argparse, hashlib, json, os, re, sys, random, datetime, unicodedata
from collections import Counter, defaultdict
EXTS = ('.txt', '.md', '.json')
FM_DATE = re.compile(r'^---\s*\n(?:.*\n)*?date:\s*["\']?(\d{4})-\d{2}-\d{2}', re.M)
NAME_DATE = re.compile(r'^(\d{4})-\d{2}-\d{2}')


def text_of(path):
    raw = open(path, 'rb').read().decode('utf-8', errors='replace')
    if path.lower().endswith('.json'):
        try:
            d = json.loads(raw)
            for k in ('text', 'content', 'body'):
                if isinstance(d, dict) and isinstance(d.get(k), str): return d[k]
        except json.JSONDecodeError: pass
        return raw
    return raw


def year_of(path, text):
    m = FM_DATE.search(text)
    if m: return int(m.group(1))
    m = NAME_DATE.match(os.path.basename(path))
    if m: return int(m.group(1))
    return datetime.datetime.fromtimestamp(os.path.getmtime(path)).year


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root'); ap.add_argument('--seed', type=int, required=True); ap.add_argument('--out', default=None); ap.add_argument('--n', type=int, default=50); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    here = os.path.abspath(os.path.dirname(__file__)); repo = os.path.abspath(os.path.join(here, '..', '..', '..', '..'))
    if a.out and os.path.abspath(a.out).startswith(repo): raise SystemExit('--out must be outside the edm-spec repository')
    if not a.dry_run and not a.out: raise SystemExit('--out is required unless --dry-run')
    items = []
    for dp, dn, fn in os.walk(a.root):
        for f in fn:
            if not f.lower().endswith(EXTS): continue
            p = os.path.join(dp, f); t = unicodedata.normalize('NFC', text_of(p).replace('\r\n', '\n').replace('\r', '\n'))
            if len(t.strip()) < 40: continue
            items.append({'rel': os.path.relpath(p, a.root), 'sha256': hashlib.sha256(t.encode('utf-8')).hexdigest(), 'length': len(t), 'year': year_of(p, t)})
            del t
    if not items: raise SystemExit('no eligible files')
    lengths = sorted(i['length'] for i in items); t1, t2 = lengths[len(lengths) // 3], lengths[2 * len(lengths) // 3]
    for i in items: i['tercile'] = 'short' if i['length'] < t1 else ('medium' if i['length'] < t2 else 'long')
    strata = defaultdict(list)
    for i in items: strata[(i['year'], i['tercile'])].append(i)
    counts = {f'{y}/{t}': len(v) for (y, t), v in sorted(strata.items())}
    print(json.dumps({'files': len(items), 'strata': counts, 'length_terciles': [t1, t2]}))
    if a.dry_run: print('dry run: nothing written'); return 0
    rng = random.Random(a.seed); keys = sorted(strata); alloc = {k: 0 for k in keys}
    total = len(items)
    for k in keys: alloc[k] = int(a.n * len(strata[k]) / total)
    rem = a.n - sum(alloc.values())
    for k in sorted(keys, key=lambda k: (a.n * len(strata[k]) / total) % 1, reverse=True)[:rem]: alloc[k] += 1
    sample = []
    for k in keys:
        pool = sorted(strata[k], key=lambda i: i['sha256']); take = min(alloc[k], len(pool))
        sample.extend(rng.sample(pool, take))
    manifest = {'seed': a.seed, 'n': len(sample), 'root_basename': os.path.basename(os.path.abspath(a.root)), 'strata': counts,
                'texts': [{'id': i['sha256'][:12], 'path': i['rel'], 'sha256': i['sha256'], 'length': i['length'], 'year': i['year'], 'tercile': i['tercile']} for i in sorted(sample, key=lambda i: i['sha256'])]}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(manifest, open(a.out, 'w', encoding='utf-8', newline='\n'), indent=1)
    print(f'manifest written to {a.out} ({len(sample)} texts; no text content stored)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
