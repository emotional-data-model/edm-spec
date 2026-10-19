"""Lexical-familiarity analysis (R31, 2026-10-19). Analysis only: no API call.

For every `emotion.primary` value word in the v0.8.3 canonical list (17) and the v0.9 recommended-vocabulary additions
from the MFOEM emotion-process list (18; REPORT.md section 5), records the word's English corpus frequency (wordfreq Zipf),
then from the existing run-3 and anchor-1 outputs computes per-value agreement measures and tests Spearman correlation
between frequency and each measure. Writes lexical-familiarity.json, lexical-familiarity.png and prints the tables that
lexical-familiarity.md carries.

Usage: python -P docs/discovery/ontology-crosswalk-2026-10/scripts/lexical_familiarity.py
"""
import json, os, re, sys
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); DOC = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(DOC)))
RUN3 = os.path.join(ROOT, 'experiments', '2026-10-18-run3'); RUN1 = os.path.join(ROOT, 'experiments', '2026-10-17'); ANCHOR = os.path.join(ROOT, 'experiments', '2026-10-18-anchor')
import wordfreq
from scipy.stats import spearmanr
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

V083 = ['joy', 'sadness', 'fear', 'anger', 'wonder', 'peace', 'tenderness', 'reverence', 'pride', 'anxiety', 'gratitude', 'longing', 'hope', 'shame', 'disappointment', 'relief', 'frustration']
# REPORT.md section 5: "Also added as codes rather than fields: ..." — the MFOEM emotion-process additions to the recommended vocabulary
MFOEM_ADD = ['disgust', 'surprise', 'contempt', 'guilt', 'interest', 'awe', 'love', 'nostalgia', 'loneliness', 'grief', 'regret', 'embarrassment', 'envy', 'boredom', 'amusement', 'contentment', 'compassion', 'trust']
WORDS = V083 + MFOEM_ADD
TIER = {w: ('v0.8.3' if w in V083 else 'MFOEM addition') for w in WORDS}
CORPUS_ARMS = ('synthetic', 'conversational', 'pepys')
RUN1_VOTERS = ['gpt-6.1-sol', 'kimi-k2.6']
MIN_ANCHOR_N = 10  # a word enters the anchor correlation when the human majority maps to it on >= 10 of the 1,000 comments
# frozen GoEmotions -> EDM mapping (experiment-plan-anchor.md section 3; identical to score_anchor.py G2E)
G2E = {'joy': 'joy', 'sadness': 'sadness', 'fear': 'fear', 'anger': 'anger', 'pride': 'pride', 'gratitude': 'gratitude', 'relief': 'relief', 'disappointment': 'disappointment',
       'nervousness': 'anxiety', 'optimism': 'hope', 'desire': 'longing', 'surprise': 'wonder', 'curiosity': 'wonder', 'admiration': 'reverence', 'caring': 'tenderness', 'love': 'tenderness',
       'embarrassment': 'shame', 'remorse': 'shame', 'annoyance': 'frustration', 'neutral': 'neutral',
       'amusement': 'other', 'approval': 'other', 'confusion': 'other', 'disapproval': 'other', 'disgust': 'other', 'excitement': 'other', 'grief': 'other', 'realization': 'other'}
GOEMOTIONS_LABELS = set(G2E)


def norm(v):
    if isinstance(v, dict): v = v.get('text')
    if isinstance(v, list): v = v[0] if v else None
    if v is None: return 'null'
    s = re.sub(r'\s+', ' ', str(v)).strip().lower()
    if s in ('', 'null', 'none', 'n/a'): return 'null'
    return s.replace(' ', '_').replace('-', '_')


def modal(labels):
    c = Counter(labels); best = max(c.values())
    return next(l for l in labels if c[l] == best), sum(1 for v in c.values() if v == best) > 1


def cohen(pairs):
    n = len(pairs)
    if n < 2: return None
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs); cb = Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if abs(1 - pe) < 1e-12: return 1.0 if po == 1.0 else None
    return (po - pe) / (1 - pe)


def load_run3_like(raw_dir, model_dir):
    """-> {text_id: {repeat: label}} for emotion.primary; valid records only."""
    out = defaultdict(dict)
    for arm in CORPUS_ARMS:
        p = os.path.join(raw_dir, model_dir, f'{arm}.jsonl')
        if not os.path.exists(p): continue
        for line in open(p, encoding='utf-8'):
            if not line.strip(): continue
            r = json.loads(line)
            if not isinstance(r.get('parsed'), dict) or r.get('transport_error') is not None: continue
            out[r['text_id']][r['repeat']] = norm(r['parsed'].get('emotion.primary'))
    return out


def run3():
    M = json.load(open(os.path.join(RUN3, 'models.json'), encoding='utf-8'))
    son = next(e['model'] for e in M['extractors'].values() if e['role'].startswith('voter re-run'))
    arms = [m for m in M['new_arms'] if os.path.isdir(os.path.join(RUN3, 'raw', m.replace('/', '__')))] + [son]
    texts = [json.loads(l)['id'] for l in open(os.path.join(RUN3, 'corpus', 'corpus_manifest.jsonl'), encoding='utf-8') if l.strip()]
    per = {m: load_run3_like(os.path.join(RUN3, 'raw'), m.replace('/', '__')) for m in arms}
    for v in RUN1_VOTERS: per[f'{v} (run 1)'] = load_run3_like(os.path.join(RUN1, 'raw'), v)
    models = list(per)
    assert len(models) == 9, models
    mod = {m: {} for m in models}; ties = Counter()
    for m in models:
        for tid in texts:
            labs = [per[m][tid][r] for r in sorted(per[m].get(tid, {}))]
            if labs:
                mod[m][tid], tie = modal(labs); ties[m] += tie
    maj = {}; plur = {}; votes = {}
    for tid in texts:
        labs = [mod[m][tid] for m in models if tid in mod[m]]
        if not labs: continue
        c = Counter(labs); top = c.most_common()
        votes[tid] = (c, len(labs))
        if top[0][1] >= 5: maj[tid] = top[0][0]
        if len(top) == 1 or top[0][1] > top[1][1]: plur[tid] = top[0][0]
    per_word = {}
    for w in WORDS:
        tids = [t for t, v in maj.items() if v == w]; ptids = [t for t, v in plur.items() if v == w]
        agree = [votes[t][0][w] / votes[t][1] for t in tids]; pagree = [votes[t][0][w] / votes[t][1] for t in ptids]
        any_mention = sum(1 for t in votes if votes[t][0].get(w))
        per_word[w] = {'n_majority': len(tids), 'share_majority': len(tids) / len(texts), 'agreement_rate': (sum(agree) / len(agree)) if agree else None,
                       'n_plurality': len(ptids), 'agreement_rate_plurality': (sum(pagree) / len(pagree)) if pagree else None,
                       'texts_with_any_model_modal': any_mention, 'model_text_modals': sum(votes[t][0].get(w, 0) for t in votes)}
    maj_dist = Counter(maj.values())
    return {'models': models, 'n_texts': len(texts), 'texts_with_majority_5of9': len(maj), 'texts_with_plurality': len(plur), 'modal_ties': dict(ties),
            'majority_distribution': dict(maj_dist.most_common()), 'majority_outside_both_lists': {k: v for k, v in maj_dist.items() if k not in WORDS},
            'per_word': per_word}


def anchor():
    M = json.load(open(os.path.join(ANCHOR, 'models_anchor.json'), encoding='utf-8'))
    sample = json.load(open(os.path.join(ANCHOR, 'data', 'sample.json'), encoding='utf-8'))
    human_raw = {c['id']: c['majority'] for c in sample}
    mod = {}
    for k, e in M['extractors'].items():
        p = os.path.join(ANCHOR, 'raw', e['model'].replace('/', '__') + '.jsonl'); per = defaultdict(dict)
        for l in open(p, encoding='utf-8'):
            if not l.strip(): continue
            r = json.loads(l)
            if r.get('transport_error') or r.get('provider_mismatch'): continue
            for i, a in (r.get('answers') or {}).items(): per[i][r['repeat']] = norm((a or {}).get('primary'))
        mod[k] = {i: modal([per[i][r] for r in sorted(per[i])])[0] for i in per if per[i]}
    models = list(mod)
    per_word = {}
    for w in WORDS:
        if w in V083:
            human = {i: (G2E[g] == w) for i, g in human_raw.items()}; basis = 'frozen G2E mapping'
        elif w in GOEMOTIONS_LABELS:
            human = {i: (g == w) for i, g in human_raw.items()}; basis = 'GoEmotions label taken directly (exploratory; outside the frozen mapping)'
        else:
            per_word[w] = {'n_human': 0, 'basis': 'no GoEmotions label', 'kappa': {}, 'kappa_mean': None, 'recall': {}, 'recall_mean': None}; continue
        n_h = sum(human.values()); kap = {}; rec = {}
        if n_h == 0:
            per_word[w] = {'n_human': 0, 'basis': basis + '; no human-majority comment maps to the word', 'kappa': {}, 'kappa_mean': None, 'recall': {}, 'recall_mean': None}; continue
        for k in models:
            pairs = [(human[i], mod[k][i] == w) for i in mod[k]]
            kap[k] = cohen(pairs)
            hit = [b for a, b in pairs if a]; rec[k] = (sum(hit) / len(hit)) if hit else None
        ks = [v for v in kap.values() if v is not None]; rs = [v for v in rec.values() if v is not None]
        per_word[w] = {'n_human': n_h, 'basis': basis, 'kappa': kap, 'kappa_mean': (sum(ks) / len(ks)) if ks else None, 'recall': rec, 'recall_mean': (sum(rs) / len(rs)) if rs else None}
    return {'models': models, 'n_items': len(sample), 'items_with_model_label': {k: len(mod[k]) for k in models}, 'per_word': per_word}


def spearman(pairs):
    xs = [a for a, b in pairs]; ys = [b for a, b in pairs]
    if len(xs) < 4: return {'n': len(xs), 'rho': None, 'p': None}
    r = spearmanr(xs, ys)
    return {'n': len(xs), 'rho': float(r.statistic), 'p': float(r.pvalue)}


def main():
    zipf = {w: wordfreq.zipf_frequency(w, 'en') for w in WORDS}
    rank = {w: i + 1 for i, w in enumerate(sorted(WORDS, key=lambda w: -zipf[w]))}
    R3 = run3(); AN = anchor()
    rows = []
    for w in WORDS:
        r = R3['per_word'][w]; a = AN['per_word'][w]
        rows.append({'word': w, 'tier': TIER[w], 'zipf': zipf[w], 'rank': rank[w], **{f'run3_{k}': v for k, v in r.items()},
                     'anchor_n_human': a['n_human'], 'anchor_basis': a['basis'], 'anchor_kappa_mean': a['kappa_mean'], 'anchor_kappa': a['kappa'], 'anchor_recall_mean': a['recall_mean']})
    def pairs(key, cond=lambda r: True): return [(r['zipf'], r[key]) for r in rows if r[key] is not None and cond(r)]
    tests = {
        'run3_share_majority_all35': spearman(pairs('run3_share_majority')),
        'run3_agreement_rate_words_with_majority': spearman(pairs('run3_agreement_rate')),
        'run3_agreement_rate_plurality': spearman(pairs('run3_agreement_rate_plurality')),
        'run3_model_text_modals_all35': spearman(pairs('run3_model_text_modals')),
        f'anchor_kappa_mean_n_ge_{MIN_ANCHOR_N}': spearman(pairs('anchor_kappa_mean', lambda r: r['anchor_n_human'] >= MIN_ANCHOR_N)),
        'anchor_kappa_mean_all_scored': spearman(pairs('anchor_kappa_mean')),
        f'anchor_recall_mean_n_ge_{MIN_ANCHOR_N}': spearman(pairs('anchor_recall_mean', lambda r: r['anchor_n_human'] >= MIN_ANCHOR_N)),
        'v083_only_run3_share': spearman(pairs('run3_share_majority', lambda r: r['tier'] == 'v0.8.3')),
        'v083_only_run3_agreement_rate': spearman(pairs('run3_agreement_rate', lambda r: r['tier'] == 'v0.8.3')),
        f'v083_only_anchor_kappa_n_ge_{MIN_ANCHOR_N}': spearman(pairs('anchor_kappa_mean', lambda r: r['tier'] == 'v0.8.3' and r['anchor_n_human'] >= MIN_ANCHOR_N)),
    }
    out = {'written': '2026-10-19', 'frequency_source': {'package': 'wordfreq', 'version': __import__('importlib.metadata').metadata.version('wordfreq'), 'function': "zipf_frequency(word, 'en')", 'wordlist': 'default (best = large English list)'},
           'words': {'v0.8.3': V083, 'mfoem_additions': MFOEM_ADD}, 'min_anchor_n': MIN_ANCHOR_N, 'run3': {k: v for k, v in R3.items() if k != 'per_word'}, 'anchor': {k: v for k, v in AN.items() if k != 'per_word'}, 'rows': rows, 'spearman': tests}
    json.dump(out, open(os.path.join(DOC, 'lexical-familiarity.json'), 'w', encoding='utf-8'), indent=1)

    # scatter: two panels, one y each (no dual axis); colour = tier (fixed order: v0.8.3 slot 1 blue, MFOEM addition slot 2 orange)
    COL = {'v0.8.3': '#2a78d6', 'MFOEM addition': '#eb6834'}; SURF = '#fcfcfb'; INK = '#0b0b0b'; INK2 = '#52514e'; GRID = '#e6e5e1'
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), facecolor=SURF)
    panels = [('run3_agreement_rate', 'Run 3: cross-vendor agreement where the 5-of-9 majority is the word', 'share of 9 models agreeing with the majority', lambda r: True,
               {'longing': (6, -11), 'boredom': (6, 3), 'sadness': (5, 7), 'disappointment': (5, -11), 'embarrassment': (-74, 5), 'tenderness': (6, -11)}),
              ('anchor_kappa_mean', f'Anchor 1: mean model–human category κ (≥ {MIN_ANCHOR_N} human-majority comments)', 'binary Cohen κ, mean of 3 models', lambda r: r['anchor_n_human'] >= MIN_ANCHOR_N,
               {'love': (-24, 8), 'surprise': (5, 8), 'shame': (5, 6), 'joy': (5, -11), 'anger': (-36, -11)})]
    for ax, (key, title, ylab, cond, offs) in zip(axes, panels):
        ax.set_facecolor(SURF)
        for s in ('top', 'right'): ax.spines[s].set_visible(False)
        for s in ('left', 'bottom'): ax.spines[s].set_color(GRID)
        ax.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(colors=INK2, labelsize=9)
        pts = [r for r in rows if r[key] is not None and cond(r)]
        for tier in ('v0.8.3', 'MFOEM addition'):
            sub = [r for r in pts if r['tier'] == tier]
            ax.scatter([r['zipf'] for r in sub], [r[key] for r in sub], s=64, color=COL[tier], edgecolor=SURF, linewidth=1.5, label=f'{tier} (n {len(sub)})', zorder=3)
        for r in pts:
            ax.annotate(r['word'], (r['zipf'], r[key]), xytext=offs.get(r['word'], (5, 4)), textcoords='offset points', fontsize=8, color=INK2)
        lo, hi = ax.get_xlim(); ax.set_xlim(lo - 0.05, hi + 0.2)
        t = tests['run3_agreement_rate_words_with_majority' if key == 'run3_agreement_rate' else f'anchor_kappa_mean_n_ge_{MIN_ANCHOR_N}']
        ax.set_title(f"{title}" + chr(10) + f"Spearman ρ {t['rho']:+.2f}, p {t['p']:.2f}, n {t['n']}", fontsize=10, color=INK, loc='left')
        ax.set_xlabel('wordfreq Zipf frequency, English (higher = more common)', fontsize=9, color=INK2); ax.set_ylabel(ylab, fontsize=9, color=INK2)
        if ax is axes[0]: ax.legend(frameon=False, fontsize=8, labelcolor=INK2, loc='lower right', bbox_to_anchor=(1.0, 0.08))
        else: ax.legend(frameon=False, fontsize=8, labelcolor=INK2, loc='upper right')
    fig.suptitle('emotion.primary value words: lexical familiarity against agreement (R31, 2026-10-19; no API calls)', fontsize=11, color=INK, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(DOC, 'lexical-familiarity.png'), dpi=160, facecolor=SURF)

    def f(x, d=2): return '—' if x is None else f'{x:.{d}f}'
    print(f"wordfreq {out['frequency_source']['version']}; run-3 models: {R3['models']}; texts {R3['n_texts']}, 5-of-9 majority on {R3['texts_with_majority_5of9']}, plurality on {R3['texts_with_plurality']}; ties {R3['modal_ties']}")
    print('majority distribution:', R3['majority_distribution']); print('outside both lists:', R3['majority_outside_both_lists'])
    print('anchor models:', AN['models'], AN['items_with_model_label'])
    print('\n| Word | Tier | Zipf | Rank | R3 majority n | R3 share | R3 agreement | R3 plurality n / agr | R3 model-text modals | A1 human n | A1 κ mean | A1 κ per model | A1 recall |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in sorted(rows, key=lambda r: r['rank']):
        kp = ' / '.join(f(v) for v in r['anchor_kappa'].values()) if r['anchor_kappa'] else '—'
        print(f"| {r['word']} | {r['tier']} | {r['zipf']:.2f} | {r['rank']} | {r['run3_n_majority']} | {f(r['run3_share_majority'], 3)} | {f(r['run3_agreement_rate'])} | {r['run3_n_plurality']} / {f(r['run3_agreement_rate_plurality'])} | {r['run3_model_text_modals']} | {r['anchor_n_human']}{'' if r['anchor_basis'].startswith('frozen') else (' †' if r['anchor_n_human'] else '')} | {f(r['anchor_kappa_mean'])} | {kp} | {f(r['anchor_recall_mean'])} |")
    print('\n| Test | n | ρ | p |\n|---|---|---|---|')
    for k, t in tests.items(): print(f"| {k} | {t['n']} | {f(t['rho'], 3)} | {f(t['p'], 3)} |")


if __name__ == '__main__':
    main()
