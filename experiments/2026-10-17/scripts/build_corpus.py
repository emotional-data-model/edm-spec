"""Build the three-arm corpus for the 2026-10-17 v0.9 field experiment (pre-registration step; no API calls).

Usage (from repo root):
  python -P experiments/2026-10-17/scripts/build_corpus.py

Arms (50 texts each):
  synthetic      experiments/2026-10-17/corpus/synthetic_texts_months_*.json (authored for this experiment; text committed)
  conversational ../deepadata-com-retrieval/eval_data/Episodic/LoCoMo/locomo10.json (2 conversations x sessions 1-10 = 20;
                 CC BY-NC 4.0 -> referenced by path + sha256, text NOT copied into edm-spec) and
                 ../deepadata-com-retrieval/tests/longmemeval/data/longmemeval_s.json (3 multi-session questions x 10 sessions = 30;
                 MIT -> referenced by path + sha256 for symmetry; text not copied)
  pepys          ../deepadata-com-retrieval/tests/pepys/corpus/scenes.json (Diary of Samuel Pepys, 1665; public domain; 5 months x 10 entries; text committed)

Outputs:
  corpus/corpus_manifest.jsonl   one record per text: id, arm, block, order, locator, sha256, word_count, text (synthetic + pepys only)
  corpus/task_a_blocks.json      retention blocks: per block the ordered entry ids and the named (ground-truth) ids with evidence
  corpus/.resolved_texts.jsonl   (gitignored) every text resolved, for the extraction runner

Selection is seeded; re-running reproduces the same manifest.
"""
import json, os, re, hashlib, random, collections, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(EXP))
RETR = os.path.normpath(os.path.join(ROOT, '..', 'deepadata-com-retrieval'))
CORPUS = os.path.join(EXP, 'corpus')
SEED = 20261017
rng = random.Random(SEED)

def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def wc(s): return len(s.split())
def rel(p): return os.path.relpath(p, ROOT).replace('\\', '/')

records, blocks = [], []

# ---------------------------------------------------------------- synthetic
syn_texts, syn_summaries = [], []
for name in sorted(os.listdir(CORPUS)):
    if name.startswith('synthetic_texts_months_') and name.endswith('.json'):
        d = json.load(open(os.path.join(CORPUS, name), encoding='utf-8'))
        syn_texts += d['texts']; syn_summaries += d['month_summaries']
syn_texts.sort(key=lambda t: t['id'])
PARTIAL = os.environ.get('CORPUS_ALLOW_PARTIAL') == '1'  # dry run before the synthetic arm exists
if not PARTIAL:
    assert len(syn_texts) == 50, f'synthetic texts: {len(syn_texts)}'
    assert len(syn_summaries) == 5
syn_path = rel(os.path.join(CORPUS, 'synthetic_texts_months_*.json'))
for t in syn_texts:
    records.append({'id': t['id'], 'arm': 'synthetic', 'block': f"syn-m{t['month']}", 'order': t['day'], 'genre': t['genre'],
                    'locator': {'path': syn_path, 'id': t['id']}, 'sha256': sha(t['text']), 'word_count': wc(t['text']), 'text': t['text']})
for m in sorted(syn_summaries, key=lambda s: s['month']):
    ids = sorted([t['id'] for t in syn_texts if t['month'] == m['month']], key=lambda i: next(t['day'] for t in syn_texts if t['id'] == i))
    named = [t['id'] for t in syn_texts if t['month'] == m['month'] and t['salient_intent']]
    assert set(m['named_ids']) == set(named), (m['month'], m['named_ids'], named)
    blocks.append({'arm': 'synthetic', 'block': f"syn-m{m['month']}", 'entries': ids, 'named': named,
                   'evidence': {'kind': 'author_month_summary', 'summary': m['summary']}})

# ---------------------------------------------------------------- LoCoMo (CC BY-NC 4.0: path reference only)
loc_path = os.path.join(RETR, 'eval_data', 'Episodic', 'LoCoMo', 'locomo10.json')
loc = json.load(open(loc_path, encoding='utf-8'))
def loc_sessions(conv):
    out = []
    for k, v in conv['conversation'].items():
        if k.startswith('session_') and not k.endswith('date_time'):
            n = int(k.split('_')[1]); out.append((n, v, conv['conversation'].get(f'{k}_date_time')))
    return sorted(out)
def loc_text(turns):
    return '\n'.join(f"{t['speaker']}: {t['text']}" + (f" [shares image: {t['blip_caption']}]" if t.get('blip_caption') else '') for t in turns)
cands = []
for c in loc:
    ss = loc_sessions(c)
    if len(ss) < 10: continue
    words = sum(wc(loc_text(v)) for n, v, dt in ss[:10])
    cands.append((words, c['sample_id']))
cands.sort()
chosen_loc = [sid for w, sid in cands[:2]]
for sid in chosen_loc:
    c = next(x for x in loc if x['sample_id'] == sid)
    ss = loc_sessions(c)[:10]
    ids = []
    for n, turns, dt in ss:
        tid = f'L{sid.replace("conv-", "")}-{n:02d}'
        txt = loc_text(turns)
        ids.append(tid)
        records.append({'id': tid, 'arm': 'conversational', 'block': f'locomo-{sid}', 'order': n, 'genre': 'locomo_dialogue_session',
                        'locator': {'path': rel(loc_path), 'sample_id': sid, 'session': f'session_{n}', 'date_time': dt, 'rendering': 'speaker: text per turn, blip_caption appended as [shares image: ...]'},
                        'sha256': sha(txt), 'word_count': wc(txt), 'text': None, '_resolved': txt})
    # named = sessions holding evidence for the benchmark's own QA items; each QA item is one probe
    probes = []
    for q in c['qa']:
        ev_sessions = sorted({int(e.split(':')[0][1:]) for e in q.get('evidence', []) if re.match(r'^D\d+:\d+$', e)})
        ev_sessions = [s for s in ev_sessions if 1 <= s <= 10]
        if ev_sessions:
            probes.append({'question': q['question'], 'category': q.get('category'), 'sessions': [f'L{sid.replace("conv-", "")}-{s:02d}' for s in ev_sessions]})
    named = sorted({s for p in probes for s in p['sessions']})
    blocks.append({'arm': 'conversational', 'block': f'locomo-{sid}', 'entries': ids, 'named': named,
                   'evidence': {'kind': 'benchmark_qa_evidence', 'probes': probes, 'scoring': 'a probe is hit when every evidence session it needs is retained; hit rate = hits / probes'}})

# ---------------------------------------------------------------- LongMemEval (MIT): 3 multi-session questions x 10 sessions
lme_path = os.path.join(RETR, 'tests', 'longmemeval', 'data', 'longmemeval_s.json')
lme = json.load(open(lme_path, encoding='utf-8'))
def user_turns(sess):
    return '\n'.join(f"User: {t['content'].strip()}" for t in sess if t.get('role') == 'user')
def answer_turn_in_user(sess):
    return any(t.get('role') == 'user' and t.get('has_answer') for t in sess)
qcands = []
for q in lme:
    if q['question_type'] != 'multi-session': continue
    ans = q['answer_session_ids']
    if not (2 <= len(ans) <= 4): continue
    ok = True; sizes = []
    for a in ans:
        s = q['haystack_sessions'][q['haystack_session_ids'].index(a)]
        u = user_turns(s)
        if not answer_turn_in_user(s) or not (80 <= wc(u) <= 600): ok = False; break
        sizes.append(wc(u))
    if ok: qcands.append((q['question_id'], len(ans), sum(sizes)))
qcands.sort(key=lambda x: (x[2], x[0]))
chosen_q = [qid for qid, n, w in qcands[:3]]
for qid in chosen_q:
    q = next(x for x in lme if x['question_id'] == qid)
    ans = list(q['answer_session_ids'])
    pool = [i for i, sidd in enumerate(q['haystack_session_ids']) if sidd not in ans and 80 <= wc(user_turns(q['haystack_sessions'][i])) <= 600]
    dis = rng.sample(pool, 10 - len(ans))
    idxs = sorted([q['haystack_session_ids'].index(a) for a in ans] + dis)  # haystack order = chronological (haystack_dates)
    ids = []
    for k, i in enumerate(idxs):
        sidd = q['haystack_session_ids'][i]; txt = user_turns(q['haystack_sessions'][i])
        tid = f'M{qid}-{k+1:02d}'
        ids.append(tid)
        records.append({'id': tid, 'arm': 'conversational', 'block': f'lme-{qid}', 'order': k + 1, 'genre': 'longmemeval_user_turns',
                        'locator': {'path': rel(lme_path), 'question_id': qid, 'haystack_session_id': sidd, 'date': q['haystack_dates'][i], 'rendering': 'user turns only, "User: " prefix'},
                        'sha256': sha(txt), 'word_count': wc(txt), 'text': None, '_resolved': txt})
    named = [f'M{qid}-{k+1:02d}' for k, i in enumerate(idxs) if q['haystack_session_ids'][i] in ans]
    blocks.append({'arm': 'conversational', 'block': f'lme-{qid}', 'entries': ids, 'named': named,
                   'evidence': {'kind': 'benchmark_answer_sessions', 'question': q['question'], 'answer': q['answer'], 'question_type': q['question_type'],
                                'scoring': 'hit rate = retained answer sessions / answer sessions'}})

# ---------------------------------------------------------------- Pepys 1665 (public domain): 5 months x 10 entries
pep_path = os.path.join(RETR, 'tests', 'pepys', 'corpus', 'scenes.json')
scenes = json.load(open(pep_path, encoding='utf-8'))
STOP = set('''the and that with this which were there their they them then than from have been upon very much more most into also would could should shall will must about after before again against because being between both during each either every here into just like made make many might much never none nothing only other over same since some such that their there these thing things those though through under until upon very what when where whether while whom whose with within without'''.split())
def toks(s):
    return {w for w in re.findall(r"[a-z]{4,}", s.lower()) if w not in STOP}
all_tok = [toks(s['scene_text']) for s in scenes]
df = collections.Counter(w for t in all_tok for w in t)
N = len(scenes)
distinct = [{w for w in t if df[w] <= max(3, int(0.05 * N))} for t in all_tok]
def backrefs(i, days=90):
    out = []
    for j in range(i + 1, N):
        if (scenes[j]['global_scene_index'] - scenes[i]['global_scene_index']) > days * 1.2: break
        shared = distinct[i] & distinct[j]
        if len(shared) >= 3: out.append({'date': scenes[j]['date'], 'shared_terms': sorted(shared)[:8]})
    return out
PEP_MONTHS = [1, 4, 6, 9, 12]
for m in PEP_MONTHS:
    pool = [i for i, s in enumerate(scenes) if s['month'] == m and 150 <= s['word_count'] <= 700]
    pick = sorted(rng.sample(pool, 10))
    ids = []
    scored = []
    for i in pick:
        s = scenes[i]; tid = f"P{s['date']}"
        ids.append(tid)
        br = backrefs(i)
        scored.append((tid, len(br), br))
        records.append({'id': tid, 'arm': 'pepys', 'block': f'pepys-m{m:02d}', 'order': i, 'genre': 'diary_entry_1665',
                        'locator': {'path': rel(pep_path), 'global_scene_index': s['global_scene_index'], 'date': s['date']},
                        'sha256': sha(s['scene_text']), 'word_count': s['word_count'], 'text': s['scene_text'], 'backref_count': len(br)})
    ranked = sorted(scored, key=lambda x: (-x[1], x[0]))
    named = [t for t, n, br in ranked[:4] if n > 0]
    blocks.append({'arm': 'pepys', 'block': f'pepys-m{m:02d}', 'entries': ids, 'named': named,
                   'evidence': {'kind': 'lexical_backreference', 'rule': 'an entry is referred back to when a later entry within ~90 days shares >= 3 distinctive terms (document frequency <= 5% of the 310 scenes, >= 4 letters, not a stopword); the 4 most-referenced entries of the month are named; ties broken by date',
                                'backrefs': {t: br for t, n, br in scored}}})

# ---------------------------------------------------------------- write
by_arm = collections.Counter(r['arm'] for r in records)
if not PARTIAL:
    assert len(records) == 150, len(records)
    assert all(v == 50 for v in by_arm.values()), by_arm
os.makedirs(CORPUS, exist_ok=True)
with open(os.path.join(CORPUS, 'corpus_manifest.jsonl'), 'w', encoding='utf-8', newline='\n') as fh:
    for r in records:
        fh.write(json.dumps({k: v for k, v in r.items() if not k.startswith('_')}, ensure_ascii=False) + '\n')
with open(os.path.join(CORPUS, '.resolved_texts.jsonl'), 'w', encoding='utf-8', newline='\n') as fh:
    for r in records:
        fh.write(json.dumps({'id': r['id'], 'arm': r['arm'], 'text': r['text'] if r['text'] is not None else r['_resolved']}, ensure_ascii=False) + '\n')
json.dump({'seed': SEED, 'k': 3, 'blocks': blocks}, open(os.path.join(CORPUS, 'task_a_blocks.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('records', len(records), dict(by_arm))
for b in blocks:
    print(f"  {b['block']:<22} entries={len(b['entries'])} named={len(b['named'])} {b['named'] if b['arm']!='conversational' else ''}")
wcs = [r['word_count'] for r in records]
print('word_count min/median/max', min(wcs), sorted(wcs)[len(wcs)//2], max(wcs))
print('locomo conversations', chosen_loc, 'longmemeval questions', chosen_q)
