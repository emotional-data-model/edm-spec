"""Human anchor on GoEmotions (experiment-plan-anchor.md section 2): build the 1,000-comment sample, stratified by the
human majority label, from the full GoEmotions release with individual rater annotations (Demszky et al. 2020;
google-research/goemotions, Apache 2.0; goemotions_{1,2,3}.csv, one row per rater x comment, 27 labels + neutral).

Eligibility (pre-registered): >= 3 raters on the comment; no rater flagged example_very_unclear; a unique plurality label
with >= 2 rater votes (the label most raters chose; a rater's vote counts once per label they chose). Majority label =
that plurality label. Allocation: proportional to the eligible count per majority label, with a floor of FLOOR per label
(capped at the label's eligible count), seeded; the remainder after floors is allocated by largest remainder.
Writes data/sample.json (comment id, text, majority label, per-rater label sets, rater count) and data/sample_stats.json.
The raw CSVs are not committed (data/goemotions_raw/ is gitignored); their sha256 is recorded.

Usage: python -I experiments/2026-10-18-anchor/scripts/sample_goemotions.py [--n 1000] [--floor 15] [--seed 20261018]
"""
import argparse, csv, hashlib, json, os, random, sys
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); RAW = os.path.join(EXP, 'data', 'goemotions_raw')
LABELS = ['admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval', 'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization', 'relief', 'remorse', 'sadness', 'surprise', 'neutral']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--n', type=int, default=1000); ap.add_argument('--floor', type=int, default=15); ap.add_argument('--seed', type=int, default=20261018)
    a = ap.parse_args()
    files = [os.path.join(RAW, f'goemotions_{i}.csv') for i in (1, 2, 3)]
    shas = {os.path.basename(p): sha(p) for p in files}
    by_id = {}
    for p in files:
        with open(p, encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f):
                c = by_id.setdefault(r['id'], {'id': r['id'], 'text': r['text'], 'subreddit': r['subreddit'], 'raters': {}, 'unclear': False})
                labs = [l for l in LABELS if r[l] == '1']
                c['raters'][r['rater_id']] = labs
                if r['example_very_unclear'] == 'True': c['unclear'] = True
    n_all = len(by_id); elig = []; why = Counter()
    for c in by_id.values():
        if len(c['raters']) < 3: why['fewer than 3 raters'] += 1; continue
        if c['unclear']: why['a rater flagged very unclear'] += 1; continue
        votes = Counter(l for labs in c['raters'].values() for l in labs)
        if not votes: why['no label'] += 1; continue
        top = votes.most_common()
        if top[0][1] < 2: why['plurality below 2 votes'] += 1; continue
        if len(top) > 1 and top[1][1] == top[0][1]: why['tied plurality'] += 1; continue
        c['majority'] = top[0][0]; c['majority_votes'] = top[0][1]; elig.append(c)
    pool = defaultdict(list)
    for c in elig: pool[c['majority']].append(c)
    rng = random.Random(a.seed)
    for l in pool: pool[l].sort(key=lambda c: c['id']); rng.shuffle(pool[l])
    counts = {l: len(pool[l]) for l in LABELS if l in pool}
    total = sum(counts.values())
    alloc = {l: min(a.floor, counts[l]) for l in counts}
    rest = a.n - sum(alloc.values())
    free = {l: counts[l] - alloc[l] for l in counts}; free_total = sum(free.values())
    quota = {l: rest * free[l] / free_total for l in counts}
    for l in counts: alloc[l] += int(quota[l])
    rem = a.n - sum(alloc.values())
    for l in sorted(counts, key=lambda l: quota[l] - int(quota[l]), reverse=True)[:rem]: alloc[l] += 1
    sample = []
    for l in LABELS:
        if l in alloc: sample.extend(pool[l][:alloc[l]])
    sample.sort(key=lambda c: c['id'])
    out = [{'id': c['id'], 'text': c['text'], 'subreddit': c['subreddit'], 'majority': c['majority'], 'majority_votes': c['majority_votes'], 'n_raters': len(c['raters']),
            'raters': {rid: labs for rid, labs in sorted(c['raters'].items())}} for c in sample]
    os.makedirs(os.path.join(EXP, 'data'), exist_ok=True)
    json.dump(out, open(os.path.join(EXP, 'data', 'sample.json'), 'w', encoding='utf-8', newline='\n'), indent=0, ensure_ascii=False)
    stats = {'source': 'GoEmotions full release (google-research/goemotions data/full_dataset/goemotions_{1,2,3}.csv), Apache 2.0', 'sha256': shas, 'comments_in_release': n_all, 'eligible': len(elig),
             'excluded': dict(why), 'eligible_per_majority_label': counts, 'allocation': alloc, 'n': len(out), 'floor': a.floor, 'seed': a.seed,
             'single_label_annotation_share': sum(1 for c in elig for labs in c['raters'].values() if len(labs) == 1) / sum(len(c['raters']) for c in elig),
             'sample_sha256': hashlib.sha256(json.dumps(out, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()}
    json.dump(stats, open(os.path.join(EXP, 'data', 'sample_stats.json'), 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in stats.items() if k != 'sha256'}, indent=1))


if __name__ == '__main__':
    sys.exit(main())
