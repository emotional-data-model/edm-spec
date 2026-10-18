"""Run-3 judge pass (experiment-plan-run3.md section 5): per text, two Opus 5.5 calls through the gateway — {summary} and
{harm, meaning, self_position, bodily_sensation} — each receiving ALL run-3 answers for the field (8 arms x 5 repeats,
indexed, arm hidden) plus three representatives from the run that classed the field: gpt-6.1-sol and kimi-k2.6 (the
two other majority components) and claude-sonnet-5-5 (framing bound only). Representative = the answer from the voter's
largest within-model equivalence class in that run's judge grouping (ties -> earliest repeat); run 1 for summary /
meaning / self_position / bodily_sensation, run 2 Arm B for harm. Null answers are pre-assigned to "null" and not sent.
Rules 1-5 (run-2 judge_system.txt verbatim); reasoning = {enabled: false} (plan section 3 note). Checkpointed to
raw/judge/<group>.jsonl; re-runs skip texts already judged. Spend -> spend_judge.json; after the first 10 calls the
pass re-projects and stops if its projection exceeds the remaining budget (plan section 9).

Usage: python -P experiments/2026-10-18-run3/scripts/judge.py [--limit N] [--concurrency 4] [--dry-run]
"""
import argparse, asyncio, json, os, re, sys, time, importlib.util
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP)
RUN1 = os.path.join(EXPS, '2026-10-17'); RUN2 = os.path.join(EXPS, '2026-10-18-run2')
sys.path.insert(0, os.path.join(RUN1, 'scripts'))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod); return mod


R3 = _load('run3_extraction', os.path.join(HERE, 'run_extraction.py'))  # MODELS, RAW, FIELDS, load_texts, ProviderOR, Spend, levers
R1S = _load('run1_score', os.path.join(RUN1, 'scripts', 'score.py'))     # flatten, get_unit, norm_text (run-1 outputs)
MODELS, RAW, FIELDS, load_texts, ProviderOR, Spend, LEVERS = R3.MODELS, R3.RAW, R3.FIELDS, R3.load_texts, R3.ProviderOR, R3.Spend, R3.LEVERS
parse_json = R3._r1.parse_json; price_of = R3.price_of

JUDGE = MODELS['judge']
ARMS = [e['model'] for e in MODELS['extractors'].values()]  # 6 new + REF + SON, in models.json order
NEW_ARMS = MODELS['new_arms']
REF = next(e['model'] for e in MODELS['extractors'].values() if e['role'].startswith('reference'))
SON = next(e['model'] for e in MODELS['extractors'].values() if e['role'].startswith('voter re-run'))
EXTENSION = [m for m in ((LEVERS.get('extension_plan_R30') or {}).get('extension_arms') or []) if (LEVERS.get('extension_plan_R30') or {}).get('executed')]  # R30: a dropped arm re-admitted once its extension has run
DROPPED = set(LEVERS.get('dropped_arms') or []) - set(EXTENSION)
NEW_ARMS_RUN = [m for m in NEW_ARMS if m not in DROPPED]  # the new arms actually run (lever 3 may drop one; R30 may re-admit it)
CORPUS_ARMS = ('synthetic', 'conversational', 'pepys')
FREE = ['narrative.harm', 'narrative.meaning', 'narrative.self_position', 'emotion.bodily_sensation', 'narrative.summary']
# order matters under the credit ceiling (plan section 9): the four-field group runs for every text before the summary control
GROUPS = {'g2_harm_meaning_self_body': ['narrative.harm', 'narrative.meaning', 'narrative.self_position', 'emotion.bodily_sensation'], 'g1_summary': ['narrative.summary']}
VOTERS_OTHER = ['gpt-6.1-sol', 'kimi-k2.6']; VOTER_SON = 'claude-sonnet-5-5'
REP_KEYS = {'gpt-6.1-sol': 'rep:gpt-6.1-sol', 'kimi-k2.6': 'rep:kimi-k2.6', 'claude-sonnet-5-5': 'rep:claude-sonnet-5-5@classing-run'}
SYS = open(os.path.join(EXP, 'prompts', 'judge_system.txt'), encoding='utf-8').read()
USR = open(os.path.join(EXP, 'prompts', 'judge_user.txt'), encoding='utf-8').read()


def norm_answer(v):
    """free-text answer as shown to the judge; a list keeps its order (rule 5); null/empty -> None (run-2 convention)."""
    if v is None: return None
    if isinstance(v, list):
        items = [norm_answer(x) for x in v]; items = [i for i in items if i]
        return '; '.join(items) if items else None
    if isinstance(v, dict): v = v.get('text')
    if v is None: return None
    s = re.sub(r'\s+', ' ', str(v)).strip()
    return s if s and s.lower() not in ('null', 'none', '[]') else None


def load_outputs(raw_dir=RAW):
    """-> outputs[model][text_id][repeat] = canon dict (valid) | None (failed: transport, provider mismatch, unparsable); counts; corpus arm per text."""
    outputs = {m: defaultdict(dict) for m in ARMS}; counts = defaultdict(lambda: defaultdict(int)); arm_of = {}; providers = defaultdict(Counter)
    for m in ARMS:
        for carm in CORPUS_ARMS:
            p = os.path.join(raw_dir, R3.arm_dir(m), f'{carm}.jsonl')
            if not os.path.exists(p): continue
            for line in open(p, encoding='utf-8'):
                if not line.strip(): continue
                r = json.loads(line); arm_of[r['text_id']] = carm
                ok = isinstance(r.get('canon'), dict) and r.get('transport_error') is None and not r.get('provider_mismatch')
                outputs[m][r['text_id']][r['repeat']] = r['canon'] if ok else None
                counts[m]['calls'] += 1; counts[m]['valid' if ok else 'invalid'] += 1
                if r.get('transport_error'): counts[m]['transport'] += 1
                elif r.get('provider_mismatch'): counts[m]['provider_mismatch'] += 1
                elif r.get('parse_error'): counts[m]['parse'] += 1
                if r.get('missing_keys'): counts[m]['missing_keys'] += 1
                if r.get('provider'): providers[m][r['provider']] += 1
    return outputs, counts, arm_of, providers


# ---- representatives from the classing runs (run 1; run 2 Arm B for harm) --------------------------------------------------
def _judge_groups(run_dir):
    groups = {}
    d = os.path.join(run_dir, 'raw', 'judge')
    for f in sorted(os.listdir(d)):
        if not f.endswith('.jsonl'): continue
        for line in open(os.path.join(d, f), encoding='utf-8'):
            if not line.strip(): continue
            r = json.loads(line)
            if r.get('groups'):
                for unit, g in r['groups'].items(): groups[(r['text_id'], unit)] = g
    return groups


def load_representatives():
    """-> reps[unit][text_id][voter] = {'text': str|None, 'class': gid, 'repeat': n, 'run': ..} for the three voters."""
    reps = {u: defaultdict(dict) for u in FREE}
    voters = VOTERS_OTHER + [VOTER_SON]
    # run 1
    g1 = _judge_groups(RUN1); out1, _, _ = R1S.load_outputs(models=voters)
    for unit in ['narrative.summary', 'narrative.meaning', 'narrative.self_position', 'emotion.bodily_sensation']:
        for v in voters:
            for tid, byrep in out1[v].items():
                g = g1.get((tid, unit))
                if g is None: continue
                cls = {rep: g.get(f'{v}#{rep}') for rep in sorted(byrep) if byrep[rep] is not None and g.get(f'{v}#{rep}') is not None}
                if not cls: continue
                cnt = Counter(cls.values()); best = max(cnt.values()); gid = next(cls[r] for r in sorted(cls) if cnt[cls[r]] == best); rep = next(r for r in sorted(cls) if cls[r] == gid)
                text = None if gid == 'null' else norm_answer(R1S.get_unit(byrep[rep], unit))
                reps[unit][tid][v] = {'text': text, 'class': gid, 'repeat': rep, 'run': 'run1', 'class_size': best, 'n_repeats': len(cls)}
    # run 2 Arm B for harm
    g2 = _judge_groups(RUN2)
    for v in voters:
        for carm in CORPUS_ARMS:
            p = os.path.join(RUN2, 'raw', v, 'B', f'{carm}.jsonl')
            byt = defaultdict(dict)
            for line in open(p, encoding='utf-8'):
                if not line.strip(): continue
                r = json.loads(line)
                if isinstance(r.get('canon'), dict) and r.get('transport_error') is None: byt[r['text_id']][r['repeat']] = r['canon']
            for tid, byrep in byt.items():
                g = g2.get((tid, 'harm'))
                if g is None: continue
                cls = {rep: g.get(f'{v}#B#{rep}') for rep in sorted(byrep) if g.get(f'{v}#B#{rep}') is not None}
                if not cls: continue
                cnt = Counter(cls.values()); best = max(cnt.values()); gid = next(cls[r] for r in sorted(cls) if cnt[cls[r]] == best); rep = next(r for r in sorted(cls) if cls[r] == gid)
                text = None if gid == 'null' else norm_answer(byrep[rep].get('harm'))
                reps['narrative.harm'][tid][v] = {'text': text, 'class': gid, 'repeat': rep, 'run': 'run2B', 'class_size': best, 'n_repeats': len(cls)}
    return reps


def answers_for(outputs, reps, tid, units):
    out = {}
    for unit in units:
        null_keys, items = [], []
        for m in ARMS:
            for rep in sorted(outputs[m].get(tid, {})):
                c = outputs[m][tid][rep]
                if c is None: continue
                key = f'{m}#{rep}'; t = norm_answer(c.get(unit))
                if t is None: null_keys.append(key)
                else: items.append((len(items), key, t))
        for v in VOTERS_OTHER + [VOTER_SON]:
            r = reps[unit].get(tid, {}).get(v)
            if r is None: continue
            key = REP_KEYS[v]
            if r['text'] is None: null_keys.append(key)
            else: items.append((len(items), key, r['text']))
        out[unit] = {'null': null_keys, 'items': items}
    return out


def build_block(ans):
    parts = []
    for unit, a in ans.items():
        if not a['items']: continue
        parts.append(f'### {unit}\n' + '\n'.join(f'{i}: {t}' for i, k, t in a['items']))
    return '\n\n'.join(parts)


def groups_from(ans, parsed):
    fields = parsed.get('fields', parsed)
    out = {}
    for unit, a in ans.items():
        g = {k: 'null' for k in a['null']}
        if a['items']:
            fj = fields.get(unit)
            if not isinstance(fj, dict) or not isinstance(fj.get('groups'), list): raise ValueError(f'missing groups for {unit}')
            seen = {}
            for gi, grp in enumerate(fj['groups']):
                for idx in grp:
                    idx = int(idx)
                    if idx in seen: raise ValueError(f'index {idx} in two groups for {unit}')
                    seen[idx] = f'g{gi}'
            if set(seen) != {i for i, k, t in a['items']}: raise ValueError(f'index set mismatch for {unit}: {len(seen)} vs {len(a["items"])}')
            for i, k, t in a['items']: g[k] = seen[i]
        out[unit] = g
    return out


async def judge_text(prov, sem, spend, tid, text, gname, units, outputs, reps, ck_path, stats, budget):
    if stats.get('abort'): return
    ans = answers_for(outputs, reps, tid, units); block = build_block(ans)
    rec = {'text_id': tid, 'group': gname, 'units': units, 'ts': time.time(), 'groups': None, 'error': None, 'usage': None, 'cost_usd': 0.0, 'provider': None, 'raw_text': None, 'n_answers': sum(len(a['items']) for a in ans.values())}
    if not block:
        rec['groups'] = {u: {k: 'null' for k in a['null']} for u, a in ans.items()}; rec['error'] = 'all null; no call'
    else:
        user = USR.format(text_id=tid, text=text, answers_block=block)
        for attempt in range(1, 4):
            try:
                async with sem:
                    raw, usage, stop, served, provider, gen_id = await prov.call(SYS, user)
                rec['reasoning_param_sent'] = prov.reasoning
                cost, listed = R3.cost_of(JUDGE, usage); spend.add(JUDGE['model'], cost, usage); stats['usd'] += cost
                rec['usage'] = usage; rec['cost_usd'] = round(cost, 6); rec['cost_list_usd'] = round(listed, 6); rec['raw_text'] = raw; rec['provider'] = provider; rec['gen_id'] = gen_id
                if (provider or '') != prov.expect_provider: raise RuntimeError(f'provider mismatch {provider!r}')
                rec['groups'] = groups_from(ans, parse_json(raw)); rec['error'] = None
                break
            except ValueError as e:
                rec['error'] = f'malformed (attempt {attempt}): {e}'
                if attempt == 3: stats['bad'] += 1
            except Exception as e:
                msg = repr(e)
                if 'Error code: 402' in msg or 'Insufficient credits' in msg:  # credit ceiling: stop the pass checkpointed (plan section 9)
                    rec['error'] = f'credit exhausted: {msg[:200]}'; stats['abort'] = True; stats['credit_stop'] = stats.get('credit_stop', 0) + 1
                    print('  judge: OpenRouter credit exhausted; pass stops checkpointed'); break
                if 'Reasoning is mandatory' in msg and prov.reasoning is not None:
                    # the Opus endpoint refuses reasoning = {enabled: false} (as the Sonnet endpoint did in the pilot): fall back to the
                    # gateway default for the rest of the pass; recorded per record and in RESULTS.md section 0.1
                    prov.reasoning = None; stats['reasoning_fallback'] = stats.get('reasoning_fallback', 0) + 1
                    print('  judge: endpoint refuses reasoning disabled; falling back to the gateway default for the remaining calls'); continue
                rec['error'] = f'transport (attempt {attempt}): {msg[:300]}'
                await asyncio.sleep(5 * attempt)
    with open(ck_path, 'a', encoding='utf-8', newline='\n') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    stats['calls'] += 1
    if budget.get('cap_usd') is not None and stats['usd'] >= budget['cap_usd'] and not stats.get('abort'):
        stats['abort'] = True; stats['cap_stop'] = True; print(f"  judge: cap USD {budget['cap_usd']} on this run reached after {stats['calls']} records (USD {stats['usd']:.2f}); pass stops checkpointed")
    if stats['calls'] == 10 or stats['calls'] % 25 == 0:
        mean = stats['usd'] / max(1, stats['calls']); proj = spend.data['total_usd'] + mean * max(0, stats['planned'] - stats['calls'])
        print(f"  judge {stats['calls']} records, ${stats['usd']:.2f} this run (bad={stats['bad']}); cumulative ${spend.data['total_usd']:.2f}; projected judge total ${proj:.2f} of remaining ${budget['remaining']:.2f}")
        if stats['calls'] == 10 and proj > budget['remaining']:
            stats['abort'] = True; print('JUDGE STOPPED: projection exceeds the remaining budget (plan section 9)')


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--limit', type=int, default=None); ap.add_argument('--concurrency', type=int, default=4); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--cap-usd', type=float, default=None, help='hard cap on the judge spend of this invocation (lever 4 / Phase A ledger): the pass stops checkpointed once reached')
    ap.add_argument('--rejudge-missing', action='store_true', help='after --rejudge: judge again only the texts whose latest groups record does not cover every arm that has outputs for the text (rate-limit failures of the supplement)')
    ap.add_argument('--rejudge', action='store_true', help='R30 supplement: judge every text again with all answers (an extension arm included); the new record supersedes the old in load_judge (last record per text wins)')
    a = ap.parse_args()
    outputs, counts, arm_of, providers = load_outputs()
    print('outputs:', {m: dict(c) for m, c in counts.items()})
    reps = load_representatives()
    print('representatives per unit (texts with all three voters):', {u: sum(1 for t in reps[u] if len(reps[u][t]) == 3) for u in FREE})
    texts = {tid: r['text'] for tid, r in load_texts().items()}
    stop = float(LEVERS.get('stop_usd', MODELS['budget_usd']))
    spent = sum(json.load(open(os.path.join(EXP, f), encoding='utf-8'))['total_usd'] for f in ('spend.json', 'spend_pilot.json') if os.path.exists(os.path.join(EXP, f)))
    sj = Spend(os.path.join(EXP, 'spend_judge.json')); budget = {'remaining': stop - spent - sj.data['total_usd'], 'cap_usd': a.cap_usd}
    print(f'stop {stop}; spent so far {spent:.2f} + judge {sj.data["total_usd"]:.2f}; remaining {budget["remaining"]:.2f}; reserve rule: start only if remaining >= 9')
    if budget['remaining'] < 9.0: print('judge pass NOT started: remaining budget below the 9 reserve'); return 2
    e = dict(JUDGE); e['endpoint'] = JUDGE['endpoint']
    prov = ProviderOR(e, {'enabled': False}); sem = asyncio.Semaphore(a.concurrency)
    stats = {'calls': 0, 'usd': 0.0, 'bad': 0, 'planned': 0}
    jd = os.path.join(RAW, 'judge'); os.makedirs(jd, exist_ok=True)
    tasks = []
    for gname, units in GROUPS.items():
        ck_path = os.path.join(jd, f'{gname}.jsonl'); done = set()
        if os.path.exists(ck_path) and not a.rejudge:
            latest = {}
            for l in open(ck_path, encoding='utf-8'):
                if l.strip():
                    r = json.loads(l)
                    if r.get('groups'): latest[r['text_id']] = r
            for tid, r in latest.items():
                if not a.rejudge_missing: done.add(tid); continue
                keys = {k for u in r['groups'].values() for k in u}
                arms_with_outputs = [m for m in ARMS if m not in DROPPED and any(v is not None for v in outputs[m].get(tid, {}).values())]
                if all(any(k.startswith(m + '#') for k in keys) for m in arms_with_outputs): done.add(tid)
        todo = [t for t in sorted(arm_of) if t not in done][:a.limit]
        print(f'{gname}: {len(todo)} texts to judge')
        stats['planned'] += len(todo)
        if not a.dry_run:
            for tid in todo: tasks.append(judge_text(prov, sem, sj, tid, texts[tid], gname, units, outputs, reps, ck_path, stats, budget))
    if a.dry_run:
        tid = sorted(arm_of)[0]; ans = answers_for(outputs, reps, tid, GROUPS['g2_harm_meaning_self_body'])
        print('dry run; example block for', tid, {u: (len(x['items']), len(x['null'])) for u, x in ans.items()}); print(build_block(ans)[:3000]); return 0
    await asyncio.gather(*tasks)
    print(f"judge done: {stats['calls']} records, ${stats['usd']:.2f} this run, bad={stats['bad']}, cumulative judge spend ${sj.data['total_usd']:.2f}")
    return 1 if stats.get('abort') else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
