"""Frozen prompts for the 2026-10-17 v0.9 field experiment. Generated from the draft v0.9 schema; written to
experiments/2026-10-17/prompts/*.txt and quoted verbatim in experiment-plan.md. No API calls.

Usage: python -P experiments/2026-10-17/scripts/prompts.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(EXP))
DRAFT = os.path.join(ROOT, 'docs', 'discovery', 'ontology-crosswalk-2026-10', 'draft-schema')
sys.path.insert(0, os.path.join(ROOT, 'docs', 'discovery', 'ontology-crosswalk-2026-10', 'scripts'))
import v09_layout as L  # noqa: E402

FRAG = {d: json.load(open(os.path.join(DRAFT, 'fragments', f'{d}.json'), encoding='utf-8')) for d in L.LAYOUT_ORDER}

# output shape per field path (what the extractor returns; EDM codings are applied afterwards by scripts/v09_layout.py)
SHAPE = {}
for dom, fields in L.LAYOUT_ORDER.items():
    for f in fields:
        path = f'{dom}.{f}'
        node = FRAG[dom]['properties']
        if f.startswith('appraisal.'): node = node['appraisal']['properties'][f.split('.')[1]]
        else: node = node[f]
        SHAPE[path] = node
def shape_of(path, node):
    t = node.get('type')
    if path in ('context.scope',): return '{"text": string|null, "direction": string|null}'
    if path == 'salience.tether': return '{"type": string|null, "referent": string|null, "stake": string|null}'
    if path == 'salience.persistence': return '{"text": string|null, "decay": string|null}'
    if path in ('emotion.valence', 'emotion.arousal', 'emotion.intensity', 'emotion.appraisal.urgency', 'emotion.appraisal.control'):
        lo, hi = {'emotion.valence': (-1, 1)}.get(path, (0, 1)); return f'{{"text": string|null, "value": number in [{lo}, {hi}]|null}}'
    if 'allOf' in node: return 'string|null  (the value word)'
    if t == ['array', 'null'] or t == 'array':
        items = node.get('items', {})
        return 'array of strings (value words)' if 'allOf' in items else 'array of strings'
    if t == ['boolean', 'null']: return 'true|false|null'
    if t == ['number', 'null']: return 'number in [0, 1]|null'
    return 'string|null'

lines = []
for dom, fields in L.LAYOUT_ORDER.items():
    lines.append(f'\n## {dom}')
    for f in fields:
        path = f'{dom}.{f}'; node = SHAPE[path]
        rec = node.get('x_recommended_values')
        if path == 'context.scope': rec = node['properties']['text'].get('x_recommended_values'); extra = f"; direction one of {node['properties']['direction']['x_recommended_values']}"
        elif path == 'salience.persistence': rec = node['properties']['text'].get('x_recommended_values'); extra = f"; decay one of {node['properties']['decay']['x_recommended_values']}"
        elif path == 'salience.tether': rec = node['properties']['type'].get('x_recommended_values'); extra = ' (applies to tether.type)'
        else: extra = ''
        desc = node.get('description', '').replace('\n', ' ')
        cons = node.get('x_constraints', '').replace('\n', ' ')
        line = f'- `{path}` -> {shape_of(path, node)}\n    {desc}'
        if cons: line += f'\n    Constraints: {cons}'
        if rec: line += f'\n    Recommended values: {", ".join(rec)}{extra}. Other wording is accepted when none fits.'
        lines.append(line)
FIELD_BLOCK = '\n'.join(lines)

EXTRACTION_SYSTEM = f"""You are an extraction engine for the Emotional Data Model (EDM) v0.9 draft, Full profile (47 affective fields).

Task: read ONE source text and fill the 47 fields below. Return ONLY a JSON object, no prose and no code fences.

Rules
1. INTERPRETATION ONLY, ATTRIBUTED. Every value must be an interpretation of what the text states, attributable to a passage in it. Do not infer traits, diagnoses, hidden motives or likely feelings. If the text does not state or unmistakably paraphrase something, the field is null (or [] for arrays).
2. Fields marked STATED-ONLY in their description (self_position, kind, arousal, appraisal.attribution, bodily_sensation, meaning, turning_point, function) are null unless the subject explicitly says it.
3. Numbers: give a `value` only when you can place the text on the scale; never invent precision. `emotion.intensity.value` is how strong the felt experience is as described (0 none to 1 overwhelming). `salience.linkage_strength` is how strongly the text links this experience to other memories or themes (0 isolated to 1 central).
4. Word choice: for coded fields use one of the recommended values when it fits; otherwise a short phrase of your own (free text is accepted). Lower case except proper names.
5. If the text is a conversation, the subject is the person whose experience is being related (the User in a companion transcript; the speakers jointly in a dialogue; the client in a clinical note). Describe their stated experience, not the assistant's or clinician's.
6. Output object: one key per field path below (use the dotted path as the key, e.g. "emotion.appraisal.urgency"), in the order given, plus a final key "field_confidence": an object mapping each NON-NULL field path to your confidence 0..1 that the value is supported by the text. Return every field key even when null.

Fields (47){FIELD_BLOCK}
"""

EXTRACTION_USER = """Source text (id: {text_id}):

<text>
{text}
</text>

Return the JSON object now."""

JUDGE_SYSTEM = """You are an equivalence judge for a repeatability study. You will see, for one source text, several short free-text answers given independently for the same EDM field by different extraction runs. Your job is to group answers that say the same thing about the text, so that agreement can be measured.

Rules
1. Two answers are EQUIVALENT when a careful reader would say they describe the same referent, event, meaning or quality of the text, even if the wording differs ("the choir recording" = "recording of the winter concert"; "sister" = "my sister"). They are NOT equivalent when they pick different referents, different causes, opposite directions, or when one is substantively more specific in a way that changes what is claimed.
2. null / empty answers form their own group ("null").
3. Judge the answers against the source text when it helps; never rewrite them.
4. Return ONLY JSON: {"fields": {"<field path>": {"groups": [[<answer index>, ...], ...], "note": "<one short clause, optional>"}, ...}}. Every answer index must appear in exactly one group. Answer indices are the integers shown before each answer."""

JUDGE_USER = """Source text (id: {text_id}):
<text>
{text}
</text>

Answers to judge, per field (index: answer):
{answers_block}

Return the JSON object now."""

RATER_SYSTEM = """You are reading an Emotional Data Model (EDM) v0.9 artifact extracted from a text you cannot see. Four fields have been blanked. Fill them from the artifact alone.

Return ONLY JSON: {"narrative.arc": <one value word or short phrase>, "salience.trajectory": <one of improving, stable, declining, integrative, or your own word>, "motivation.need": <one of belonging, mastery, autonomy, safety, meaning, authenticity, or your own word>, "narrative.valence_shift": <short phrase, e.g. "dread to relief">}

Recommended arc values: {arc_values}. Use null where the artifact gives no basis."""

RATER_USER = """Artifact:
{artifact_json}

Return the JSON object now."""

def main():
    out = os.path.join(EXP, 'prompts'); os.makedirs(out, exist_ok=True)
    for name, txt in (('extraction_system.txt', EXTRACTION_SYSTEM), ('extraction_user.txt', EXTRACTION_USER), ('judge_system.txt', JUDGE_SYSTEM),
                      ('judge_user.txt', JUDGE_USER), ('rater_system.txt', RATER_SYSTEM.replace('{arc_values}', ', '.join(sorted(L.CANONICAL['arc'])))), ('rater_user.txt', RATER_USER)):
        open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n').write(txt)
    print('prompts written to', out, '| extraction system chars:', len(EXTRACTION_SYSTEM), '| fields:', len(SHAPE))

if __name__ == '__main__':
    main()
