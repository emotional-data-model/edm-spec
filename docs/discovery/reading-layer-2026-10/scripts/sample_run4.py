"""Run-4 public sample (experiment-plan-run4.md section 2): 50 of the 150 public texts of runs 1-3, stratified by corpus arm
(synthetic 17, conversational 17, pepys 16), drawn from the run-3 corpus manifest (ids and sha256 only; no text is read or
written). Deterministic (seed 20261019). Prints the ids; with --out writes {id, arm, sha256} to a JSON file.

Usage: python -I docs/discovery/reading-layer-2026-10/scripts/sample_run4.py [--seed 20261019] [--out experiments/<date>-run4/corpus/sample_ids.json]
"""
import argparse, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
MANIFEST = os.path.join(ROOT, 'experiments', '2026-10-18-run3', 'corpus', 'corpus_manifest.jsonl')
QUOTA = {'synthetic': 17, 'conversational': 17, 'pepys': 16}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--seed', type=int, default=20261019); ap.add_argument('--out', default=None)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(MANIFEST, encoding='utf-8') if l.strip()]
    by_arm = {}
    for r in rows: by_arm.setdefault(r['arm'], []).append(r)
    assert set(by_arm) == set(QUOTA), sorted(by_arm)
    rng = random.Random(a.seed); out = []
    for arm in ('synthetic', 'conversational', 'pepys'):
        pool = sorted(by_arm[arm], key=lambda r: r['id']); pick = rng.sample(pool, QUOTA[arm])
        out.extend({'id': r['id'], 'arm': arm, 'sha256': r['sha256']} for r in sorted(pick, key=lambda r: r['id']))
    print(json.dumps({'seed': a.seed, 'n': len(out), 'per_arm': {k: sum(1 for o in out if o['arm'] == k) for k in QUOTA}, 'ids': [o['id'] for o in out]}))
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        json.dump({'seed': a.seed, 'source_manifest': os.path.relpath(MANIFEST, ROOT), 'texts': out}, open(a.out, 'w', encoding='utf-8', newline='\n'), indent=1)
        print('written', a.out)


if __name__ == '__main__':
    sys.exit(main())
