"""Progress / error summary of raw/<model>/<arm>.jsonl checkpoints. Usage: python -P experiments/2026-10-17/scripts/progress.py"""
import json, os, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE)
tot = collections.Counter(); err = collections.Counter(); cost = collections.Counter(); lat = collections.defaultdict(list); arms = collections.Counter()
for p in glob.glob(os.path.join(EXP, 'raw', '*', '*.jsonl')):
    parts = os.path.normpath(p).split(os.sep); m = parts[-2]; arm = parts[-1][:-6]
    if m in ('pilot', 'judge', 'rater'): continue
    for l in open(p, encoding='utf-8'):
        if not l.strip(): continue
        r = json.loads(l); tot[m] += 1; cost[m] += r['cost_usd']; lat[m].append(r['latency_s']); arms[(m, arm)] += 1
        if r.get('transport_error'): err[(m, 'transport')] += 1
        elif r.get('parse_error'): err[(m, 'parse')] += 1
        elif r['parsed'] and sum(1 for k in r['parsed'] if k != 'field_confidence') != 47: err[(m, 'fields!=47')] += 1
for m in sorted(tot):
    ls = sorted(lat[m])
    print(f"{m:<18} n={tot[m]:>4}/750 cost=${cost[m]:.2f} median_lat={ls[len(ls)//2]}s arms={ {a: n for (mm, a), n in arms.items() if mm == m} } errors={ {k[1]: v for k, v in err.items() if k[0] == m} }")
print('records', sum(tot.values()), '/ 3000; cost so far', round(sum(cost.values()), 2))
