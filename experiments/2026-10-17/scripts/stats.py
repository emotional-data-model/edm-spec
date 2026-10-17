"""Agreement statistics for the 2026-10-17 experiment: Fleiss' kappa (variable raters per subject) and ICC(2,1).
Run `python -P stats.py` to execute the textbook checks (Fleiss 1971 table -> 0.210; Shrout & Fleiss 1979 -> ICC(2,1) 0.29)."""
import math
from collections import Counter

def fleiss_kappa(ratings):
    """ratings: list of subjects; each subject is a list of category labels (one per rater; raters may vary per subject).
    Subjects with < 2 labels are dropped. Returns (kappa, info). kappa is None when P_e == 1 and agreement is perfect
    (a single category everywhere): agreement is total but kappa is undefined; the caller decides how to report it."""
    subj = [s for s in ratings if len(s) >= 2]
    dropped = len(ratings) - len(subj)
    if not subj: return None, {'subjects': 0, 'dropped': dropped, 'categories': 0, 'P_bar': None, 'P_e': None}
    cats = sorted({c for s in subj for c in s}, key=str)
    tot = Counter(); P = []
    for s in subj:
        n = len(s); cnt = Counter(s); tot.update(cnt)
        P.append((sum(v * v for v in cnt.values()) - n) / (n * (n - 1)))
    N = sum(tot.values())
    p = {c: tot[c] / N for c in cats}
    P_bar = sum(P) / len(P); P_e = sum(v * v for v in p.values())
    info = {'subjects': len(subj), 'dropped': dropped, 'categories': len(cats), 'P_bar': P_bar, 'P_e': P_e, 'category_shares': p}
    if abs(1 - P_e) < 1e-12: return None, info
    return (P_bar - P_e) / (1 - P_e), info

def icc2_1(matrix):
    """matrix: list of rows (subjects) x columns (raters), numbers, complete (no None). ICC(2,1), Shrout & Fleiss 1979."""
    n = len(matrix); k = len(matrix[0]) if n else 0
    if n < 2 or k < 2: return None
    grand = sum(sum(r) for r in matrix) / (n * k)
    row_means = [sum(r) / k for r in matrix]
    col_means = [sum(matrix[i][j] for i in range(n)) / n for j in range(k)]
    SSR = k * sum((m - grand) ** 2 for m in row_means)
    SSC = n * sum((m - grand) ** 2 for m in col_means)
    SST = sum((matrix[i][j] - grand) ** 2 for i in range(n) for j in range(k))
    SSE = SST - SSR - SSC
    MSR = SSR / (n - 1); MSC = SSC / (k - 1); MSE = SSE / ((n - 1) * (k - 1))
    denom = MSR + (k - 1) * MSE + k * (MSC - MSE) / n
    if abs(denom) < 1e-12: return None
    return (MSR - MSE) / denom

def pairwise_same_rate(labels):
    """fraction of unordered pairs among labels that are identical (labels = group ids); None if < 2."""
    n = len(labels)
    if n < 2: return None
    same = sum(1 for i in range(n) for j in range(i + 1, n) if labels[i] == labels[j])
    return same / (n * (n - 1) / 2)

def modal(labels):
    """most frequent label; ties -> the earliest occurring label among the tied."""
    if not labels: return None
    cnt = Counter(labels); best = max(cnt.values())
    for l in labels:
        if cnt[l] == best: return l

def median(xs):
    xs = sorted(xs); n = len(xs)
    if not n: return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2

if __name__ == '__main__':
    # Fleiss (1971) worked example as tabulated on Wikipedia: 10 subjects, 14 raters, 5 categories; kappa = 0.210
    table = [[0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1], [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7]]
    ratings = [[c for c, n in enumerate(row) for _ in range(n)] for row in table]
    k, info = fleiss_kappa(ratings)
    assert abs(k - 0.210) < 0.0015, k
    # Shrout & Fleiss (1979) table: 6 targets x 4 judges; ICC(2,1) = 0.29
    sf = [[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]]
    icc = icc2_1(sf)
    assert abs(icc - 0.29) < 0.005, icc
    assert pairwise_same_rate(['a', 'a', 'b']) == 1 / 3 and modal(['b', 'a', 'a', 'b']) == 'b' and median([3, 1, 2]) == 2
    print(f'stats checks passed: fleiss={k:.3f} (0.210), icc2_1={icc:.3f} (0.29)')
