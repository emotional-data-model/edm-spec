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
Rule 3: canonical values are a recommended vocabulary (x_recommended_values), not an enum on text; the EDM code on
https://emotionaldatamodel.org/vocab/<field>/v1 IS enumerated, so a canonical claim is checkable while free text stays legal.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v09_layout as L

repo, out_dir = sys.argv[1:3]
BASE = 'https://deepadata.com/schemas/edm/v0.9.0-draft'
V08 = 'https://deepadata.com/schemas/edm/v0.8.0/fragments'
FRAG = BASE + '/fragments'
D083 = {f['path']: f for f in L.FIELDS_083}
DEP = {}
for f, v, to, why in L.DEPRECATED_VALUES: DEP.setdefault(f, []).append({'value': v, 'replaced_by': to, 'reason': why})

def desc_of(*paths):
    return ' / '.join(D083[p]['description'] for p in paths)

# field path -> (description, x_constraints)
DESC = {
 'narrative.subject': (desc_of('core.anchor'), D083['core.anchor']['constraints']),
 'narrative.trigger': (desc_of('core.spark'), D083['core.spark']['constraints']),
 'narrative.harm': (desc_of('core.wound'), D083['core.wound']['constraints']),
 'narrative.drive': (desc_of('core.fuel'), D083['core.fuel']['constraints']),
 'narrative.integration': (desc_of('core.bridge'), D083['core.bridge']['constraints']),
 'narrative.summary': (desc_of('core.narrative'), D083['core.narrative']['constraints']),
 'narrative.meaning': (desc_of('constellation.expressed_insight'), D083['constellation.expressed_insight']['constraints']),
 'narrative.identity_link': (desc_of('constellation.identity_thread'), D083['constellation.identity_thread']['constraints']),
 'narrative.turning_point': (desc_of('constellation.transformational_pivot'), 'true or false; null when the subject does not say'),
 'narrative.arc': ('The story movement(s) the experience represents. A list so that a structural reading (v0.8.3 arc_type) and a trajectory reading (v0.8.3 narrative_arc) of the same memory can both be stored; order carries no meaning.', 'Each item is text + codings; EDM vocab arc/v1 unites the former arc_type and narrative_arc value sets. Free text accepted.'),
 'narrative.valence_shift': (desc_of('milky_way.tone_shift'), D083['milky_way.tone_shift']['constraints']),
 'narrative.self_position': ("The subject's own expressed lens on themselves within the story: the position they say they occupy (e.g. \"the one who holds it together\", \"the person who finally said no\"). STATED-ONLY: recorded only when the subject says it or paraphrases it unmistakably; never assigned from the plot, the emotion or an archetype catalogue.", 'Short phrase in the subject\'s own terms; NULL when not stated. Replaces narrative_archetype (the Mark & Pearson 12 are not used). Optional codings: McAdams imago (open label), agency / communion, Hermans I-position; all relation=related.'),
 'emotion.primary': (desc_of('constellation.emotion_primary'), D083['constellation.emotion_primary']['constraints']),
 'emotion.secondary': ('Secondary emotional nuances that add depth to the primary emotion, including any complex or layered state (v0.8.3 emotion_subtone + higher_order_emotion)', '0-5 items; free text; each item may carry codings with a per-coding confidence'),
 'emotion.kind': ('Whether the subject describes the affect as an episode with an object (emotion), a diffuse state without one (mood), a felt bodily quality (feeling), or a standing disposition. Stated-only; NULL when the subject does not distinguish.', 'emotion -> MFOEM:000001; mood -> MFOEM:000193; feeling -> MFOEM:000006; disposition -> MFOEM:000199'),
 'emotion.valence': (desc_of('gravity.valence'), 'text positive / negative / mixed; value in [-1, 1] on EmotionML fsre-dimensions#valence, populated only by an extraction that produces it (never derived from text)'),
 'emotion.arousal': ('The stated activation level of the experience (keyed up vs calm), independent of valence and of intensity. Stated-only.', 'text low / medium / high; value in [0, 1] on EmotionML pad-dimensions#arousal; NULL when not expressed'),
 'emotion.intensity': (desc_of('gravity.emotional_weight'), 'value in [0, 1] (v0.8.3 emotional_weight carried as-is); text is an optional ordinal label'),
 'emotion.meta': (desc_of('constellation.meta_emotional_state'), D083['constellation.meta_emotional_state']['constraints']),
 'emotion.bodily_sensation': (desc_of('constellation.somatic_signature'), D083['constellation.somatic_signature']['constraints']),
 'emotion.temporal_profile': (desc_of('constellation.temporal_rhythm'), 'Canonical: ' + ', '.join(D083['constellation.temporal_rhythm']['canonical_values']) + '. looping and cyclic are deprecated (code to recurring). Free text accepted.'),
 'emotion.appraisal.urgency': (desc_of('impulse.urgency'), 'text calm / elevated / pressing / acute; value in [0, 1] on EmotionML ema-appraisals#urgency, never derived from text'),
 'emotion.appraisal.control': (desc_of('impulse.agency_level'), 'text low / medium / high; value in [0, 1] on EmotionML scherer-appraisals#control, never derived from text'),
 'emotion.appraisal.attribution': ('To whom or what the subject attributes the cause of the event ("I blamed myself", "it was just bad luck"). Explicit content only.', 'self -> MFOEM:000076 / EmotionML agent-self; other -> MFOEM:000078 / agent-other; chance -> MFOEM:000077 / agent-nature'),
 'context.event': (desc_of('milky_way.event_type'), D083['milky_way.event_type']['constraints']),
 'context.event_category': ('Coded companion to context.event: the content category of the event as the subject describes it.', 'Singer & Blagov / Thorne & McLean categories: ' + ', '.join(L.NEW_VOCAB['event_category']) + ' (labels knowledge-reconstructed; REPORT.md section 9)'),
 'context.place': (desc_of('milky_way.location_context'), D083['milky_way.location_context']['constraints']),
 'context.people': (desc_of('milky_way.associated_people'), D083['milky_way.associated_people']['constraints']),
 'context.relationship': (desc_of('constellation.relational_dynamics'), 'Canonical: ' + ', '.join(D083['constellation.relational_dynamics']['canonical_values']) + '. friend, couple, grief, self_reflection are deprecated. Free text accepted.'),
 'context.relationship_model': ("Coded companion to context.relationship: the relational model the subject's account of the relationship instantiates (Fiske).", ', '.join(L.NEW_VOCAB['relationship_model'])),
 'context.life_stage': (desc_of('constellation.temporal_context'), 'Canonical: ' + ', '.join(D083['constellation.temporal_context']['canonical_values'])),
 'context.scope': ('The perspective through which the experience is narrated (v0.8.3 relational_perspective) and whether the impulse is self-directed, relational or expansive beyond self (v0.8.3 directionality)', 'text: self / partner / family / friends / community / humanity; direction: inward / outward / transcendent; codings on EDM vocab scope/v1 (Bronfenbrenner nested systems as companion codes)'),
 'salience.memory_type': (desc_of('constellation.memory_type'), 'Canonical: ' + ', '.join(D083['constellation.memory_type']['canonical_values']) + '. legacy_artifact is deprecated (an object tether, not a memory type).'),
 'salience.tether': ('What the experience is emotionally anchored to: its kind (v0.8.3 tether_type), the concrete referent (v0.8.3 symbolic_anchor) and what is at stake in it (v0.8.3 gravity_type)', 'type: canonical ' + ', '.join(D083['gravity.tether_type']['canonical_values']) + ', free text accepted; referent and stake: free text'),
 'salience.retrieval_cues': ('Cues that reactivate the memory: what continues to resonate (v0.8.3 core.echo), sensory or symbolic triggers (recall_triggers) and compact retrieval hooks (retrieval_keys), concatenated in that order by migration', 'Short phrases; order carries no meaning'),
 'salience.themes': (desc_of('gravity.nearby_themes'), D083['gravity.nearby_themes']['constraints']),
 'salience.recurrence': (desc_of('gravity.recurrence_pattern'), 'Canonical: cyclical, isolated, chronic; emerging is deprecated. Free text accepted. NULL when the pattern cannot be determined.'),
 'salience.persistence': ('How long the emotion is expected to stay: the perceived stickiness (v0.8.3 viscosity) and the expected decay rate (v0.8.3 temporal_decay)', 'text: low / medium / high / enduring (fluid deprecated); decay: fast / moderate / slow; codings on EDM vocab persistence/v1 (transient / short / enduring / chronic) by the fixed recode table in v09_layout.py'),
 'salience.linkage_strength': (desc_of('gravity.strength_score'), D083['gravity.strength_score']['constraints']),
 'salience.function': ('Why the subject says the memory matters: to guide action (directive), to define the self (self), or to connect with others (social). Multi-valued; stated-only.', 'Pillemer 1992 / Bluck 2003 memory functions'),
 'salience.resilience': (desc_of('gravity.resilience_markers'), D083['gravity.resilience_markers']['constraints']),
 'salience.trajectory': (desc_of('gravity.adaptation_trajectory'), 'Canonical: improving, stable, declining, integrative; emerging is deprecated'),
 'motivation.action_tendency': (desc_of('impulse.drive_state'), 'Canonical: ' + ', '.join(D083['impulse.drive_state']['canonical_values']) + ' (Frijda action tendencies applied as codes; value words unchanged)'),
 'motivation.need': (desc_of('impulse.motivational_orientation'), 'Canonical: ' + ', '.join(D083['impulse.motivational_orientation']['canonical_values']) + ' (SDT needs applied as codes)'),
 'motivation.temporal_focus': (desc_of('impulse.temporal_focus'), 'past / present / future'),
 'motivation.risk_posture': (desc_of('impulse.risk_posture'), 'cautious / balanced / bold'),
 'motivation.coping': (desc_of('impulse.coping_style'), 'Canonical: ' + ', '.join(D083['impulse.coping_style']['canonical_values']) + ' (Ways of Coping and Gross families applied as codes). Free text accepted.'),
 'trait.attachment_style': (desc_of('impulse.attachment_style') + ' - as stated by the subject for this experience; never aggregated into a person-level classification by the artifact', 'secure / anxious / avoidant / disorganized; codings on EDM vocab attachment_style/v1 with Ainsworth / Main letter codes as display'),
 'trait.regulation_state': (desc_of('impulse.regulation_state') + ' - as stated by the subject for this experience', 'regulated / wavering / dysregulated'),
}
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
    branches = [ref('dimension'), {'properties': {'value': {'minimum': lo, 'maximum': hi}}}]
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
 'valence': dimension('emotion.valence'), 'arousal': dimension('emotion.arousal'), 'intensity': annotate({'allOf': [ref('dimension'), {'properties': {'value': {'minimum': 0, 'maximum': 1}}}]}, 'emotion.intensity'),
 'meta': text('emotion.meta'), 'bodily_sensation': text('emotion.bodily_sensation'), 'temporal_profile': coded('emotion.temporal_profile'),
 'appraisal': {'description': 'Appraisal dimensions stated by the subject (Scherer / EmotionML appraisal vocabularies)', 'type': ['object', 'null'], 'additionalProperties': False,
               'x_profiles': ['full'],
               'properties': {'urgency': dimension('emotion.appraisal.urgency'), 'control': dimension('emotion.appraisal.control'), 'attribution': coded('emotion.appraisal.attribution')}},
}, 'The affect itself: category, valence, arousal, intensity, meta-emotion, bodily sensation, temporal profile and appraisal (v0.8.3 constellation emotion fields + gravity.valence / emotional_weight + impulse urgency / agency_level).')

context = fragment('context', {
 'event': text('context.event'), 'event_category': coded('context.event_category'), 'place': text('context.place'), 'people': text_list('context.people'),
 'relationship': coded('context.relationship'), 'relationship_model': coded('context.relationship_model'), 'life_stage': coded('context.life_stage'),
 'scope': annotate({'type': ['object', 'null'], 'additionalProperties': False, 'required': ['text'],
                    'properties': {'text': {'type': ['string', 'null'], 'x_recommended_values': D083['constellation.relational_perspective']['canonical_values']},
                                   'direction': {'type': ['string', 'null'], 'x_recommended_values': D083['impulse.directionality']['canonical_values'], 'x_profiles': ['full']},
                                   'codings': {'type': 'array', 'items': {'allOf': [ref('coding'), edm_codes('scope')]}}}}, 'context.scope'),
}, 'Where, when, with whom and in what relational frame (v0.8.3 milky_way + the relational fields of constellation).')

salience = fragment('salience', {
 'memory_type': coded('salience.memory_type'),
 'tether': annotate({'type': ['object', 'null'], 'additionalProperties': False, 'required': ['type'],
                     'properties': {'type': {'allOf': [ref('coded'), {'properties': {'codings': {'items': edm_codes('tether')}}}]},
                                    'referent': {'type': ['string', 'null'], 'description': 'The concrete object, place or element that concentrates the meaning (v0.8.3 symbolic_anchor)'},
                                    'stake': {'type': ['string', 'null'], 'description': 'What is at stake in the tether (v0.8.3 gravity_type; Lazarus ego-involvement)', 'x_profiles': ['full']}}}, 'salience.tether'),
 'retrieval_cues': text_list('salience.retrieval_cues'), 'themes': text_list('salience.themes'), 'recurrence': coded('salience.recurrence'),
 'persistence': annotate({'type': ['object', 'null'], 'additionalProperties': False, 'required': ['text'],
                          'properties': {'text': {'type': ['string', 'null'], 'x_recommended_values': [v for v in D083['gravity.viscosity']['canonical_values'] if v != 'fluid']},
                                         'decay': {'type': ['string', 'null'], 'x_recommended_values': D083['gravity.temporal_decay']['canonical_values']},
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
    props['extensions'] = {'$ref': INFRA['extensions'], 'x_draft_note': 'Optional in every profile so that migration can preserve cut and out-of-profile text (the v0.8 composites do not list extensions).'}
    required = ['meta', *domains.keys(), 'governance', 'telemetry'] + (['system', 'crosswalks'] if profile == 'full' else [])
    n_aff = len(fields)
    return {
     '$schema': 'http://json-schema.org/draft-07/schema#', '$id': f'{BASE}/edm.{profile}.schema.json',
     'title': f'EDM v0.9.0 {profile.capitalize()} Profile (DRAFT, discovery)',
     'description': f'DRAFT composite for the v0.9 layout proposed in docs/discovery/ontology-crosswalk-2026-10/v0.9-proposal.md. {n_aff} affective fields over {len(domains)} affective domains; the trait block is not included (opt-in via partner manifest). Not normative; not under VERSIONING_POLICY until adopted.',
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
