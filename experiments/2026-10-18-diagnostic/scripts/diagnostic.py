"""Diagnostic on run-1 outputs (founder instruction 2026-10-18): for each of the six core slots, every text where the four
extractors' modal answers are not all judge-equivalent (from experiments/2026-10-17 raw/<model> + raw/judge) gets ONE
Opus 5.5 call that classifies the disagreement as (a) multiple valid referents, (b) extractor wrong, (c) granularity only,
(d) null vs populated. Judge calls only; no extraction. Checkpointed per call to raw/diagnostic.jsonl; cap USD 8.

Usage (repo root; ANTHROPIC_API_KEY from .env):
  python -P experiments/2026-10-18-diagnostic/scripts/diagnostic.py --build-only      # items.json + counts + projection, no call
  python -P experiments/2026-10-18-diagnostic/scripts/diagnostic.py --limit 12         # pilot
  python -P experiments/2026-10-18-diagnostic/scripts/diagnostic.py                    # full, resumes from the checkpoint
"""
import argparse, asyncio, json, os, sys, time, random, hashlib
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); DIAG = os.path.dirname(HERE); EXPS = os.path.dirname(DIAG)
RUN1 = os.path.join(EXPS, '2026-10-17'); ROOT = os.path.dirname(EXPS)
sys.path.insert(0, os.path.join(RUN1, 'scripts'))
from score import load_outputs, load_judge, get_unit, norm_text, EXTRACTORS  # noqa: E402
from run_extraction import Provider, Spend, price_of, parse_json, MODELS  # noqa: E402
from stats import modal  # noqa: E402

CAP_USD = 8.0
JUDGE = MODELS['judge']  # claude-opus-5-5; never an extractor
SLOTS = ['narrative.subject', 'narrative.trigger', 'narrative.harm', 'narrative.drive', 'narrative.integration', 'salience.retrieval_cues']
OLD = {'narrative.subject': 'anchor', 'narrative.trigger': 'spark', 'narrative.harm': 'wound', 'narrative.drive': 'fuel', 'narrative.integration': 'bridge', 'salience.retrieval_cues': 'echo'}
LABELS = ['A', 'B', 'C', 'D']
SYS = open(os.path.join(DIAG, 'prompts', 'diagnostic_system.txt'), encoding='utf-8').read()
USR = open(os.path.join(DIAG, 'prompts', 'diagnostic_user.txt'), encoding='utf-8').read()
ITEMS = os.path.join(DIAG, 'items.json'); CK = os.path.join(DIAG, 'raw', 'diagnostic.jsonl')


def definitions():
    """the six slot blocks verbatim from the run-1 extraction prompt."""
    lines = open(os.path.join(RUN1, 'prompts', 'extraction_system.txt'), encoding='utf-8').read().split('\n')
    out = {}
    for s in SLOTS:
        i = next(k for k, l in enumerate(lines) if l.startswith(f'- `{s}`'))
        j = i + 1
        while j < len(lines) and not lines[j].startswith('- `') and not lines[j].startswith('## '): j += 1
        out[s] = '\n'.join(lines[i:j]).rstrip()
    return out


def build_items():
    """every (text, slot) whose four modal judge classes are not all the same; the modal class is computed exactly as
    score.py computes the cross-model representative (modal over the judge labels of the valid repeats, null included)."""
    outputs, counts, arm_of = load_outputs(); judge = load_judge()
    items = []
    for tid in sorted(arm_of):
        for slot in SLOTS:
            g = judge.get((tid, slot))
            if g is None: continue
            per = {}
            for m in EXTRACTORS:
                reps = [(rep, flat) for rep, flat in sorted(outputs[m].get(tid, {}).items()) if flat is not None]
                labels = [g.get(f'{m}#{rep}') for rep, flat in reps]
                pairs = [(rf, l) for rf, l in zip(reps, labels) if l is not None]
                if not pairs: continue
                mode = modal([l for rf, l in pairs])
                answers = [norm_text(get_unit(flat, slot)) for (rep, flat), l in pairs if l == mode]
                cnt = Counter(answers)
                rep_answer = None if mode == 'null' else cnt.most_common(1)[0][0]
                variants = [] if mode == 'null' else [a for a, n in cnt.most_common() if a != rep_answer]
                per[m] = {'class': mode, 'answer': rep_answer, 'variants': variants[:2], 'n_in_class': len(answers), 'n_valid': len(pairs)}
            if len(per) < 2 or len({p['class'] for p in per.values()}) == 1: continue
            rnd = random.Random(hashlib.sha256(f'{tid}|{slot}'.encode()).hexdigest())
            order = list(EXTRACTORS); rnd.shuffle(order)
            items.append({'text_id': tid, 'arm': arm_of[tid], 'slot': slot, 'label_of': {m: LABELS[i] for i, m in enumerate(order)}, 'per_extractor': per})
    return items


def answers_block(item):
    rows = []
    for m, lab in sorted(item['label_of'].items(), key=lambda kv: kv[1]):
        p = item['per_extractor'][m]
        if p['class'] == 'null': a = 'null'
        else:
            a = json.dumps(p['answer'], ensure_ascii=False)
            if p['variants']: a += '  (same class, other wording: ' + '; '.join(json.dumps(v, ensure_ascii=False) for v in p['variants']) + ')'
        rows.append(f"{lab}: {a} — {p['n_in_class']}/{p['n_valid']}")
    return '\n'.join(rows)


def validate(parsed, item):
    cls = parsed.get('class')
    if cls not in ('a', 'b', 'c', 'd'): raise ValueError(f'class {cls!r}')
    labs = set(item['label_of'].values())
    wrong = parsed.get('wrong') or []
    if not isinstance(wrong, list) or not set(map(str, wrong)) <= labs: raise ValueError(f'wrong {wrong!r}')
    if cls == 'b' and not wrong: raise ValueError('class b with no wrong extractor')
    if cls == 'd' and parsed.get('null_supported') not in (True, False): raise ValueError('class d without null_supported')
    return {'class': cls, 'wrong': sorted(set(map(str, wrong))), 'referents': parsed.get('referents') or [], 'most_specific': parsed.get('most_specific'),
            'null_present': bool(parsed.get('null_present')), 'null_supported': parsed.get('null_supported'), 'evidence': parsed.get('evidence'), 'rationale': parsed.get('rationale')}


async def judge_item(prov, sem, spend, item, text, defs, stats, lock):
    # the user message is split at "Field:" so that the source text (first block) is a cache breakpoint shared by the
    # text's slot calls, which run in sequence (pilot gate, see RESULTS.md section 0); the rendered content is unchanged
    head, rest = USR.split('\nField:', 1)
    text_block = head.format(text_id=item['text_id'], text=text)
    rest_block = ('Field:' + rest).format(slot=item['slot'], old=OLD[item['slot']], definition=defs[item['slot']], answers_block=answers_block(item))
    user = text_block + '\n' + rest_block
    rec = {'text_id': item['text_id'], 'slot': item['slot'], 'arm': item['arm'], 'label_of': item['label_of'], 'ts': time.time(), 'verdict': None, 'error': None,
           'usage': None, 'cost_usd': 0.0, 'raw_text': None, 'request_sha256': hashlib.sha256((JUDGE['model'] + '\n' + SYS + '\n' + user).encode('utf-8')).hexdigest()}
    for attempt in range(1, 4):
        if spend.data['total_usd'] >= CAP_USD: rec['error'] = 'cap reached; no call'; stats['capped'] += 1; break
        try:
            async with sem:
                r = await prov.client.messages.create(model=prov.model, max_tokens=600, output_config={'effort': 'low'},
                                                      system=[{'type': 'text', 'text': SYS, 'cache_control': {'type': 'ephemeral'}}],
                                                      messages=[{'role': 'user', 'content': [{'type': 'text', 'text': text_block + '\n', 'cache_control': {'type': 'ephemeral'}},
                                                                                             {'type': 'text', 'text': rest_block}]}])
            raw = ''.join(b.text for b in r.content if b.type == 'text'); u = r.usage
            usage = {'input_tokens': u.input_tokens, 'output_tokens': u.output_tokens, 'cached_input_tokens': getattr(u, 'cache_read_input_tokens', 0) or 0, 'cache_write_tokens': getattr(u, 'cache_creation_input_tokens', 0) or 0}
            cost = price_of(JUDGE, usage)
            async with lock: spend.add(JUDGE['model'], cost, usage)
            stats['usd'] += cost; rec['usage'] = usage; rec['cost_usd'] = round(cost, 6); rec['raw_text'] = raw
            rec['verdict'] = validate(parse_json(raw), item); rec['error'] = None
            break
        except ValueError as e:  # malformed verdict: one more try with the same input (the judge is instrumentation, not a subject)
            rec['error'] = f'malformed (attempt {attempt}): {e}'
            if attempt == 3: stats['bad'] += 1
        except Exception as e:
            rec['error'] = f'transport (attempt {attempt}): {repr(e)[:200]}'
            await asyncio.sleep(5 * attempt)
    if rec['error'] != 'cap reached; no call':
        with open(CK, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    stats['calls'] += 1
    if stats['calls'] % 25 == 0: print(f"  {stats['calls']} records, ${stats['usd']:.2f} this run, cumulative ${spend.data['total_usd']:.2f} (bad={stats['bad']})")


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--build-only', action='store_true'); ap.add_argument('--limit', type=int, default=None); ap.add_argument('--concurrency', type=int, default=4)
    ap.add_argument('--assume-cost', type=float, default=None, help='per-call USD used for the start projection instead of the checkpoint mean (pilot gate; the USD 8 hard cap still applies per call)')
    a = ap.parse_args()
    items = build_items(); defs = definitions()
    os.makedirs(os.path.dirname(CK), exist_ok=True)
    json.dump({'built_at': time.strftime('%Y-%m-%d %H:%M:%S'), 'source': 'experiments/2026-10-17 raw/<model>/*.jsonl + raw/judge/*.jsonl', 'slots': SLOTS, 'definitions': defs, 'n_items': len(items), 'items': items},
              open(ITEMS, 'w', encoding='utf-8', newline='\n'), indent=1, ensure_ascii=False)
    c = Counter((i['slot'], i['arm']) for i in items)
    print(f'{len(items)} disagreement items (text x slot) of {6 * 150}')
    for s in SLOTS: print(f"  {s:<26} syn {c[(s, 'synthetic')]:>3}  conv {c[(s, 'conversational')]:>3}  pepys {c[(s, 'pepys')]:>3}  total {sum(c[(s, x)] for x in ('synthetic', 'conversational', 'pepys')):>3}")
    spend = Spend(os.path.join(DIAG, 'spend.json'))
    done = set()
    if os.path.exists(CK):
        for l in open(CK, encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r.get('verdict'): done.add((r['text_id'], r['slot']))
    todo = [i for i in items if (i['text_id'], i['slot']) not in done]
    if a.limit: todo = todo[:a.limit]
    mean = a.assume_cost or (spend.data['total_usd'] / spend.data['calls'] if spend.data['calls'] else None)
    print(f"done {len(done)}; to do {len(todo)}; spent ${spend.data['total_usd']:.2f}" + (f"; mean ${mean:.4f}/call; projected total ${spend.data['total_usd'] + mean * len(todo):.2f} (cap {CAP_USD})" if mean else ''))
    if a.build_only or not todo: return
    if mean and spend.data['total_usd'] + mean * len(todo) > CAP_USD: print('projection exceeds cap; not starting'); return
    texts = {json.loads(l)['id']: json.loads(l)['text'] for l in open(os.path.join(RUN1, 'corpus', '.resolved_texts.jsonl'), encoding='utf-8')}
    prov = Provider(JUDGE); sem = asyncio.Semaphore(a.concurrency); lock = asyncio.Lock(); stats = {'calls': 0, 'usd': 0.0, 'bad': 0, 'capped': 0}
    by_text = {}
    for i in todo: by_text.setdefault(i['text_id'], []).append(i)

    async def run_text(tid, its):  # the slot calls of one text in sequence so that its cached text block is reused
        for i in its: await judge_item(prov, sem, spend, i, texts[tid], defs, stats, lock)
    await asyncio.gather(*(run_text(tid, its) for tid, its in by_text.items()))
    print(f"diagnostic done: {stats['calls']} records, ${stats['usd']:.2f} this run, bad={stats['bad']}, capped={stats['capped']}, cumulative ${spend.data['total_usd']:.2f}")


if __name__ == '__main__':
    asyncio.run(main())
