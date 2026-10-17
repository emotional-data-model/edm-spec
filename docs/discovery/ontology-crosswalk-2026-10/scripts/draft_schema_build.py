"""Generate the DRAFT v0.9 JSON Schema (draft-07) under draft-schema/ from the field map in v09_layout.py.

Usage:
  python -I scripts/draft_schema_build.py <repo-root> draft-schema

Writes fragments/{common,narrative,emotion,context,salience,motivation,trait,telemetry}.json and the three
composites edm.v0.9.{essential,extended,full}.schema.json. Unchanged infrastructure domains (governance, system,
crosswalks, extensions) are referenced from the published v0.8.0 fragments by their $id; meta is copied from the
v0.8 composite of the same profile with the version pattern widened to 0.9.x(-draft). Discovery output, not normative.

Shapes (fragments/common.json):
  coded      {text, codings[]}            text is the interpretation; codings are optional and additive
  coded_list [coded, ...]
  dimension  {text, value, codings[]}     ordinal label beside a number; neither is derived from the other
  coding     {system, version, code, display, relation, confidence}   FHIR R4 Coding + EDM relation
Rule 1 of v0.9-proposal.md section 4 is enforced: a coding is only allowed when text (or, for a dimension, value) is present.
Rule 3 (ruling 2026-10-17): canonical values are a recommended vocabulary (x_recommended_values), not an enum on text; the EDM
code on https://emotionaldatamodel.org/vocab/<field>/v1 IS enumerated, so a canonical claim is checkable while free text stays
legal. Rulings 2026-10-17 also fix: Essential = 12 fields (+ salience.retrieval_cues); extensions allowed in all three composites.
Rulings 2026-10-18 (rulings-2026-10-18.md; annotations only, nothing removed, no profile change): every scored unit carries x_run1
(pooled run-1 statistics); pooled-cut units outside the six core slots x_comparability "extractor-bound", the four interpretive
units "interpretive", narrative.integration / identity_link "null-driven" (R4); the six core slots x_status "pending run 2
(prompt test)" (R2 / R3); the value member of valence / arousal / urgency / control x_status "removed by R5", kept on
intensity and linkage_strength (R5).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v09_layout as L

repo, out_dir = sys.argv[1:3]
BASE = 'https://deepadata.com/schemas/edm/v0.9.0-draft'
V08 = 'https://deepadata.com/schemas/edm/v0.8.0/fragments'
FRAG = BASE + '/fragments'
D083 = L.D083
DEP = L.DEP
DESC = L.DESC  # moved to v09_layout.py (single source for the draft schema and the crosswalk record; ruling 2026-10-18 step 2)

VOCAB_OF = {  # coded / dimension field -> EDM vocabulary name
 'narrative.arc': 'arc', 'emotion.primary': 'emotion', 'emotion.secondary': 'emotion', 'emotion.kind': 'kind', 'emotion.valence': 'valence',
 'emotion.arousal': 'arousal', 'emotion.temporal_profile': 'temporal_profile', 'emotion.appraisal.urgency': 'urgency', 'emotion.appraisal.control': 'control',
 'emotion.appraisal.attribution': 'attribution', 'context.event_category': 'event_category', 'context.relationship': 'relationship',
 'context.relationship_model': 'relationship_model', 'context.life_stage': 'life_stage', 'context.scope': 'scope', 'salience.memory_type': 'memory_type',
 'salience.tether': 'tether', 'salience.recurrence': 'recurrence', 'salience.persistence': 'persistence', 'salience.function': 'function',
 'salience.trajectory': 'trajectory', 'motivation.action_tendency': 'action_tendency', 'motivation.need': 'need', 'motivation.temporal_focus': 'temporal_focus',
 'motivation.risk_posture': 'risk_posture', 'motivation.coping': 'coping', 'trait.attachment_style': 'attachment_style', 'trait.regulation_state': 'regulation_state',
}
RANGE = {'emotion.valence': (-1, 1), 'emotion.arousal': (0, 1), 'emotion.intensity': (0, 1), 'emotion.appraisal.urgency': (0, 1), 'emotion.appraisal.control': (0, 1)}
PROFILES_OF = {p: [prof for prof, fs in L.PROFILES_09.items() if p in fs] for p in L.ALL_09}

def ref(name): return {'$ref': f'{FRAG}/common.json#/definitions/{name}'}
def nullable(t): return {'type': [t, 'null']}

def edm_codes(vocab):
    """Constrain the code when the coding system is the EDM vocabulary of this field."""
    values = sorted(L.CANONICAL[vocab])
    return {'if': {'properties': {'system': {'const': L.VOCAB.format(field=vocab)}}, 'required': ['system']},
            'then': {'properties': {'code': {'enum': values}}}}

def annotate(schema, path, extra=None):
    d, c = DESC[path]
    schema = {'description': d, 'x_constraints': c, 'x_profiles': PROFILES_OF.get(path, []), **schema}
    v = VOCAB_OF.get(path)
    if v:
        schema['x_edm_vocabulary'] = L.VOCAB.format(field=v)
        rec = sorted(L.CANONICAL[v] - {x['value'] for x in DEP.get(path, [])})
        schema['x_recommended_values'] = rec
        if DEP.get(path): schema['x_deprecated_values'] = DEP[path]
    schema.update(L.run1_annotations(path))  # rulings 2026-10-18 R2 / R4 / R5: annotations only
    if extra: schema.update(extra)
    return schema

def coded(path):
    v = VOCAB_OF[path]
    return annotate({'allOf': [ref('coded'), {'properties': {'codings': {'items': edm_codes(v)}}}]}, path)
def coded_list(path, max_items=None):
    v = VOCAB_OF[path]
    s = {'type': ['array', 'null'], 'items': {'allOf': [ref('coded'), {'properties': {'codings': {'items': edm_codes(v)}}}]}}
    if max_items: s['maxItems'] = max_items
    return annotate(s, path)
def dimension(path):
    lo, hi = RANGE[path]
    branches = [ref('dimension'), {'properties': {'text': L.run1_annotations(path + '.text'), 'value': {'minimum': lo, 'maximum': hi, **L.run1_annotations(path + '.value')}}}]
    if path in VOCAB_OF: branches.append({'properties': {'codings': {'items': edm_codes(VOCAB_OF[path])}}})
    return annotate({'allOf': branches}, path)
def text(path): return annotate(nullable('string'), path)
def text_list(path): return annotate({'type': ['array', 'null'], 'items': {'type': 'string'}}, path)

def fragment(title, props, description=None, required=None):
    f = {'$schema': 'http://json-schema.org/draft-07/schema#', '$id': f'{FRAG}/{title.lower()}.json', 'title': f'EDM {title.upper()} Domain (v0.9 DRAFT)'}
    if description: f['description'] = description
    f.update({'type': 'object', 'properties': props, 'additionalProperties': False})
    if required: f['required'] = required
    return f

common = {
 '$schema': 'http://json-schema.org/draft-07/schema#', '$id': f'{FRAG}/common.json', 'title': 'EDM v0.9 DRAFT shared shapes',
 'description': 'coded = text + codings; dimension = text + value + codings; coding = FHIR R4 Coding (system, version, code, display) plus an EDM relation. Text is the interpretation; codings are optional, additive and may disagree; a coding never replaces the text.',
 'definitions': {
  'coding': {'type': 'object', 'additionalProperties': False, 'required': ['system', 'code'],
   'properties': {'system': {'type': 'string', 'format': 'uri', 'description': 'Code system URI (EDM vocabulary, OBO PURL, EmotionML vocabulary, or an EDM xref placeholder)'},
                  'version': {'type': ['string', 'null'], 'description': 'Code-system version as published by its owner'},
                  'code': {'type': 'string'}, 'display': {'type': ['string', 'null']},
                  'relation': {'type': 'string', 'enum': ['exact', 'broader', 'narrower', 'related'], 'default': 'exact', 'description': 'How the EDM text relates to the target concept (SKOS mapping sense)'},
                  'confidence': {'type': ['number', 'null'], 'minimum': 0, 'maximum': 1, 'description': 'Extractor confidence in this coding (EmotionML confidence attribute)'}}},
  'codings': {'type': 'array', 'items': {'$ref': '#/definitions/coding'}, 'default': []},
  'coded': {'type': 'object', 'additionalProperties': False, 'required': ['text'],
   'properties': {'text': {'type': ['string', 'null'], 'description': 'The interpretation, in the value words of the field; mandatory when the field is populated'}, 'codings': {'$ref': '#/definitions/codings'}},
   'if': {'properties': {'codings': {'minItems': 1}}, 'required': ['codings']}, 'then': {'properties': {'text': {'type': 'string'}}},
   'x_rule': 'codings are only allowed when text is present (v0.9-proposal.md section 4 rule 1)'},
  'dimension': {'type': 'object', 'additionalProperties': False, 'required': ['text', 'value'],
   'properties': {'text': {'type': ['string', 'null'], 'description': 'Ordinal label'}, 'value': {'type': ['number', 'null'], 'description': 'Numeric value on the scale named by the EmotionML coding; never derived from text by migration'}, 'codings': {'$ref': '#/definitions/codings'}},
   'if': {'properties': {'codings': {'minItems': 1}}, 'required': ['codings']}, 'then': {'anyOf': [{'properties': {'text': {'type': 'string'}}}, {'properties': {'value': {'type': 'number'}}}]},
   'x_rule': 'codings are only allowed when text or value is present'},
 }}

narrative = fragment('narrative', {
 'subject': text('narrative.subject'), 'trigger': text('narrative.trigger'), 'harm': text('narrative.harm'), 'drive': text('narrative.drive'),
 'integration': text('narrative.integration'), 'summary': text('narrative.summary'), 'meaning': text('narrative.meaning'),
 'identity_link': text('narrative.identity_link'), 'turning_point': annotate(nullable('boolean'), 'narrative.turning_point'),
 'arc': coded_list('narrative.arc', 3), 'valence_shift': text('narrative.valence_shift'), 'self_position': text('narrative.self_position'),
}, 'What the story is and what the subject says it means (v0.8.3 core + the narrative fields of constellation and milky_way).')

emotion = fragment('emotion', {
 'primary': coded('emotion.primary'), 'secondary': coded_list('emotion.secondary', 5), 'kind': coded('emotion.kind'),
 'valence': dimension('emotion.valence'), 'arousal': dimension('emotion.arousal'), 'intensity': annotate({'allOf': [ref('dimension'), {'properties': {'text': L.run1_annotations('emotion.intensity.text'), 'value': {'minimum': 0, 'maximum': 1, **L.run1_annotations('emotion.intensity.value')}}}]}, 'emotion.intensity'),
 'meta': text('emotion.meta'), 'bodily_sensation': text('emotion.bodily_sensation'), 'temporal_profile': coded('emotion.temporal_profile'),
 'appraisal': {'description': 'Appraisal dimensions stated by the subject (Scherer / EmotionML appraisal vocabularies)', 'type': ['object', 'null'], 'additionalProperties': False,
               'x_profiles': ['full'],
               'properties': {'urgency': dimension('emotion.appraisal.urgency'), 'control': dimension('emotion.appraisal.control'), 'attribution': coded('emotion.appraisal.attribution')}},
}, 'The affect itself: category, valence, arousal, intensity, meta-emotion, bodily sensation, temporal profile and appraisal (v0.8.3 constellation emotion fields + gravity.valence / emotional_weight + impulse urgency / agency_level).')

context = fragment('context', {
 'event': text('context.event'), 'event_category': coded('context.event_category'), 'place': text('context.place'), 'people': text_list('context.people'),
 'relationship': coded('context.relationship'), 'relationship_model': coded('context.relationship_model'), 'life_stage': coded('context.life_stage'),
 'scope': annotate({'type': ['object', 'null'], 'additionalProperties': False, 'required': ['text'],
                    'properties': {'text': {'type': ['string', 'null'], 'x_recommended_values': D083['constellation.relational_perspective']['canonical_values'], **L.run1_annotations('context.scope.text')},
                                   'direction': {'type': ['string', 'null'], 'x_recommended_values': D083['impulse.directionality']['canonical_values'], 'x_profiles': ['full'], **L.run1_annotations('context.scope.direction')},
                                   'codings': {'type': 'array', 'items': {'allOf': [ref('coding'), edm_codes('scope')]}}}}, 'context.scope'),
}, 'Where, when, with whom and in what relational frame (v0.8.3 milky_way + the relational fields of constellation).')

salience = fragment('salience', {
 'memory_type': coded('salience.memory_type'),
 'tether': annotate({'type': ['object', 'null'], 'additionalProperties': False, 'required': ['type'],
                     'properties': {'type': {'allOf': [ref('coded'), {'properties': {'codings': {'items': edm_codes('tether')}}}], **L.run1_annotations('salience.tether.type')},
                                    'referent': {'type': ['string', 'null'], 'description': 'The concrete object, place or element that concentrates the meaning (v0.8.3 symbolic_anchor)', **L.run1_annotations('salience.tether.referent')},
                                    'stake': {'type': ['string', 'null'], 'description': 'What is at stake in the tether (v0.8.3 gravity_type; Lazarus ego-involvement)', 'x_profiles': ['full'], **L.run1_annotations('salience.tether.stake')}}}, 'salience.tether'),
 'retrieval_cues': text_list('salience.retrieval_cues'), 'themes': text_list('salience.themes'), 'recurrence': coded('salience.recurrence'),
 'persistence': annotate({'type': ['object', 'null'], 'additionalProperties': False, 'required': ['text'],
                          'properties': {'text': {'type': ['string', 'null'], 'x_recommended_values': [v for v in D083['gravity.viscosity']['canonical_values'] if v != 'fluid'], **L.run1_annotations('salience.persistence.text')},
                                         'decay': {'type': ['string', 'null'], 'x_recommended_values': D083['gravity.temporal_decay']['canonical_values'], **L.run1_annotations('salience.persistence.decay')},
                                         'codings': {'type': 'array', 'items': {'allOf': [ref('coding'), edm_codes('persistence')]}}}}, 'salience.persistence'),
 'linkage_strength': annotate({'type': ['number', 'null'], 'minimum': 0, 'maximum': 1}, 'salience.linkage_strength'),
 'function': coded_list('salience.function', 3), 'resilience': text_list('salience.resilience'), 'trajectory': coded('salience.trajectory'),
}, 'Why and how the experience stays retrievable and what it is bound to (v0.8.3 gravity + memory_type / symbolic_anchor + core.echo).')

motivation = fragment('motivation', {x: coded(f'motivation.{x}') for x in L.LAYOUT_ORDER['motivation']},
                      'The behavioural direction the subject expresses (v0.8.3 impulse minus the appraisal, scope and trait fields).')

trait = fragment('trait', {'attachment_style': coded('trait.attachment_style'), 'regulation_state': coded('trait.regulation_state')},
                 'OPT-IN. Person-level readings that no canonical profile includes (theoretical-conflicts.md section 5). A partner profile opts in by listing trait.* in its included_fields; a validator for a profile that has not opted in rejects this block. Values are recorded only as stated for this experience; the artifact never aggregates them into a classification of the person.')

telemetry = json.load(open(os.path.join(repo, 'schema', 'fragments', 'telemetry.json'), encoding='utf-8'))
telemetry['$id'] = f'{FRAG}/telemetry.json'; telemetry['title'] = 'EDM TELEMETRY Domain (v0.9 DRAFT)'
telemetry['properties']['extraction_provider']['enum'] = ['anthropic', 'openai', 'google', 'kimi', 'open_weight', 'other', None]
telemetry['properties']['extraction_provider']['x_draft_note'] = 'google, open_weight and other added so the experiment-plan.md runs can be recorded; v0.8.3 enum is anthropic / openai / kimi'
telemetry['properties']['field_confidence'] = {'description': "Extractor confidence per populated field, keyed by field path (e.g. \"emotion.primary\": 0.92), after EmotionML's confidence attribute. Infrastructure, not an affective field; excluded from the seal hash like the rest of telemetry.",
                                               'type': ['object', 'null'], 'propertyNames': {'pattern': '^(narrative|emotion|context|salience|motivation|trait)\\.[a-z_.]+$'},
                                               'additionalProperties': {'type': 'number', 'minimum': 0, 'maximum': 1}}

# ---- composites ----
DOMAIN_FRAG = {'narrative': narrative, 'emotion': emotion, 'context': context, 'salience': salience, 'motivation': motivation}
INFRA = {'governance': f'{V08}/governance.json', 'system': f'{V08}/system.json', 'crosswalks': f'{V08}/crosswalks.json', 'extensions': f'{V08}/extensions.json'}

def composite(profile):
    fields = L.PROFILES_09[profile]
    v08 = json.load(open(os.path.join(repo, 'schema', f'edm.v0.8.{profile}.schema.json'), encoding='utf-8'))
    meta = v08['properties']['meta']; meta['properties']['version']['pattern'] = '^0\\.9\\.[0-9]+(-draft)?$'
    domains = {}
    for dom in DOMAIN_FRAG:
        keys = sorted({p.split('.')[1] for p in fields if p.startswith(dom + '.')}, key=lambda k: L.LAYOUT_ORDER[dom].index(k if k != 'appraisal' else 'appraisal.urgency'))
        if not keys: continue
        req = [k for k in keys if f'{dom}.{k}' in L.ESSENTIAL_09]
        narrowing = {'type': 'object', 'propertyNames': {'enum': keys}}
        if req: narrowing['required'] = req
        domains[dom] = {'allOf': [{'$ref': f'{FRAG}/{dom}.json'}, narrowing], 'x_fields': [p for p in fields if p.startswith(dom + '.')]}
    props = {'meta': meta, **domains, 'governance': {'$ref': INFRA['governance']}, 'telemetry': {'$ref': f'{FRAG}/telemetry.json'}}
    if profile == 'full':
        props['system'] = {'$ref': INFRA['system']}; props['crosswalks'] = {'$ref': INFRA['crosswalks']}
    props['extensions'] = {'$ref': INFRA['extensions'], 'x_note': 'Allowed (optional) in every profile by ruling 2026-10-17, so that migration can preserve cut and out-of-profile text. The v0.8 composites do not list extensions (README known limitation).'}
    required = ['meta', *domains.keys(), 'governance', 'telemetry'] + (['system', 'crosswalks'] if profile == 'full' else [])
    n_aff = len(fields)
    return {
     '$schema': 'http://json-schema.org/draft-07/schema#', '$id': f'{BASE}/edm.{profile}.schema.json',
     'title': f'EDM v0.9.0 {profile.capitalize()} Profile (DRAFT, discovery)',
     'description': f'DRAFT composite for the v0.9 layout proposed in docs/discovery/ontology-crosswalk-2026-10/v0.9-proposal.md. {n_aff} affective fields over {len(domains)} affective domains; the trait block is not included (opt-in via partner manifest); extensions allowed; text of coded fields is a recommended vocabulary (string), codings on the EDM vocabulary are enumerated. Not normative; not under VERSIONING_POLICY until adopted.',
     'x_affective_field_count': n_aff, 'x_affective_fields': fields,
     'type': 'object', 'required': required, 'additionalProperties': False, 'properties': props,
    }

os.makedirs(os.path.join(out_dir, 'fragments'), exist_ok=True)
def dump(obj, path):
    with open(path, 'w', encoding='utf-8', newline='\n') as fh: json.dump(obj, fh, indent=2, ensure_ascii=False); fh.write('\n')
dump(common, os.path.join(out_dir, 'fragments', 'common.json'))
for name, frag in {**DOMAIN_FRAG, 'trait': trait, 'telemetry': telemetry}.items(): dump(frag, os.path.join(out_dir, 'fragments', f'{name}.json'))
for p in ('essential', 'extended', 'full'): dump(composite(p), os.path.join(out_dir, f'edm.v0.9.{p}.schema.json'))
print('draft schema written:', {p: len(L.PROFILES_09[p]) for p in L.PROFILES_09}, 'fragments:', sorted(os.listdir(os.path.join(out_dir, 'fragments'))))
