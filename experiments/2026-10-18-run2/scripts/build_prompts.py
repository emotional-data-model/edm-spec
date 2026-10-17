"""Run-2 prompts, generated from the frozen plan and the audited crosswalk record (experiment-plan-run2.md section 4).
Arm A field block is built from draft-crosswalk/v0.8.3_to_v0.9.0.json field_map[].run2_arm_a (+ `narrative` from
schema/fragments/core.json), compared byte-for-byte with schema/fragments/core.json and with the plan's section 4.2
block; Arm B block, shared header and user message are read verbatim from the plan's fenced blocks. Judge system prompt =
run-1 judge_system.txt + rule 5 (plan section 5). A mismatch aborts. No API calls.

Usage: python -P experiments/2026-10-18-run2/scripts/build_prompts.py
"""
import json, os, re, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); EXPS = os.path.dirname(EXP); ROOT = os.path.dirname(EXPS)
RUN1 = os.path.join(EXPS, '2026-10-17'); DISC = os.path.join(ROOT, 'docs', 'discovery', 'ontology-crosswalk-2026-10')
PLAN = open(os.path.join(DISC, 'experiment-plan-run2.md'), encoding='utf-8').read()
CORE = json.load(open(os.path.join(ROOT, 'schema', 'fragments', 'core.json'), encoding='utf-8'))['properties']
XW = json.load(open(os.path.join(DISC, 'draft-crosswalk', 'v0.8.3_to_v0.9.0.json'), encoding='utf-8'))
ARM_A_FIELDS = ['anchor', 'spark', 'wound', 'fuel', 'bridge', 'echo']


def fenced(section):
    """first ~~~text block after the heading that starts with `section` (e.g. '### 4.2')."""
    i = PLAN.index('\n' + section)
    m = re.search(r'~~~text\n(.*?)\n~~~', PLAN[i:], re.S)
    return m.group(1)


def arm_a_block():
    byname = {}
    for f in XW['field_map']:
        a = f.get('run2_arm_a')
        if a: byname[a['name']] = a
    assert sorted(byname) == sorted(ARM_A_FIELDS), sorted(byname)
    lines = []
    for n in ARM_A_FIELDS:
        a = byname[n]; node = CORE[n]
        if a['description'] != node['description'] or a['constraints'] != node['x_constraints']:
            raise SystemExit(f'Arm A mismatch with schema/fragments/core.json on {n}')
        lines.append(f"- `{n}` -> string|null\n    {a['description']}\n    Constraints: {a['constraints']}")
    nar = CORE['narrative']
    lines.append(f"- `narrative` -> string|null\n    {nar['description']}\n    Constraints: {nar['x_constraints']}")
    return '\n'.join(lines)


def main():
    header = fenced('### 4.1'); a_plan = fenced('### 4.2'); b_block = fenced('### 4.3'); user = fenced('### 4.4')
    a_block = arm_a_block()
    if a_block != a_plan: raise SystemExit('Arm A block generated from the crosswalk record differs from experiment-plan-run2.md section 4.2')
    rule5 = re.search(r'~~~text\n(5\. LENGTH IS NOT A DIFFERENCE.*?)\n~~~', PLAN, re.S).group(1)
    judge_sys = open(os.path.join(RUN1, 'prompts', 'judge_system.txt'), encoding='utf-8').read().rstrip('\n') + '\n' + rule5 + '\n'
    judge_usr = open(os.path.join(RUN1, 'prompts', 'judge_user.txt'), encoding='utf-8').read()
    out = {'arm_a_system.txt': header + '\n' + a_block + '\n', 'arm_b_system.txt': header + '\n' + b_block + '\n', 'extraction_user.txt': user + '\n',
           'judge_system.txt': judge_sys, 'judge_user.txt': judge_usr}
    pd = os.path.join(EXP, 'prompts'); os.makedirs(pd, exist_ok=True)
    for n, t in out.items():
        open(os.path.join(pd, n), 'w', encoding='utf-8', newline='\n').write(t)
        print(f'{n:<22} {len(t):>6} chars sha256 {hashlib.sha256(t.encode()).hexdigest()[:16]}')
    print('Arm A verbatim against schema/fragments/core.json and plan section 4.2: OK')


if __name__ == '__main__':
    main()
