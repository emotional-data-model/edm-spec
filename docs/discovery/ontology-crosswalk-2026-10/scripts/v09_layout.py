"""v0.9 discovery layout: the proposed field map (v0.8.3 -> v0.9.0), the draft crosswalk record,
and a migration demonstration proving that artifact text is unchanged by the relayout.

Usage:
  python -I scripts/v09_layout.py <examples-dir> <out-crosswalk.json> <out-migration-example.json> [<migrated-out-dir>]

<examples-dir> holds the seven v0.8.3 artifacts (synthetic-examples/ on this branch). The migration example is built
from example-full-profile.json; with <migrated-out-dir> every artifact in the directory is migrated, pruned to its
(base) profile's v0.9 manifest, and written there for validation against draft-schema/ (an unpruned copy goes to
<migrated-out-dir>/unpruned/ so the profile-agnostic relayout can be validated too).

Discovery only. Nothing here is normative; the crosswalk is written with status "draft".
"""
import json, sys, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DISC = os.path.dirname(HERE)
VOCAB = 'https://emotionaldatamodel.org/vocab/{field}/v1'
XREF = 'https://emotionaldatamodel.org/xref/v1/{fw}'
MFOEM_SYS = 'http://purl.obolibrary.org/obo/mfoem.owl'
MFOEM_VER = '2025-07-31'
EML = 'http://www.w3.org/TR/emotion-voc/xml#{voc}'
EML_VER = '2014-04-01'
LEGACY_EXT = 'org.emotionaldatamodel.migration'

mfoem = json.load(open(os.path.join(DISC, 'mfoem_classes.json'), encoding='utf-8'))
MF = {c['label']: c['id'] for c in mfoem['classes'] if c.get('label') and c['id'].startswith('MFOEM') and not c['deprecated']}

# ---------------------------------------------------------------------------
# 1. Field map. One row per v0.8.3 field (57) plus the new v0.9 fields.
#    action: rename | move | merge | cut | trait
#    shape : text | list | coded (text+codings) | coded_list | dimension (text+value+codings) | bool | number | object
# ---------------------------------------------------------------------------
FIELD_MAP = [
 # core -> narrative
 ('core.anchor',                 'narrative.subject',          'rename', 'text',   'EmotionML reference@targetedAt; OCC object'),
 ('core.spark',                  'narrative.trigger',          'rename', 'text',   'EmotionML reference@triggeredBy'),
 ('core.wound',                  'narrative.harm',             'rename', 'text',   'Lazarus & Folkman harm/loss appraisal; MFOEM:000106 appraisal of loss'),
 ('core.fuel',                   'narrative.drive',            'rename', 'text',   'Panksepp SEEKING; SDT intrinsic motivation'),
 ('core.bridge',                 'narrative.integration',      'rename', 'text',   'Singer & Blagov integrative meaning'),
 ('core.echo',                   'salience.retrieval_cues',    'merge',  'list',   'Tulving retrieval cue; first element of the merged list'),
 ('core.narrative',              'narrative.summary',          'rename', 'text',   'the narrative text itself'),
 # constellation -> emotion / narrative / context / salience
 ('constellation.emotion_primary',        'emotion.primary',            'rename', 'coded',      'MFOEM emotion process; EmotionML category'),
 ('constellation.emotion_subtone',        'emotion.secondary',          'rename', 'coded_list', 'EmotionML multiple categories'),
 ('constellation.higher_order_emotion',   'emotion.secondary',          'merge',  'coded_list', 'appended to secondary[]'),
 ('constellation.meta_emotional_state',   'emotion.meta',               'rename', 'text',       'meta-emotion (Gottman et al. 1996)'),
 ('constellation.interpersonal_affect',   None,                         'cut',    None,         'no framework home beyond EI competencies; text preserved in extensions'),
 ('constellation.narrative_arc',          'narrative.arc',              'merge',  'coded_list', 'Booker / McAdams; arc becomes a list so both readings survive'),
 ('constellation.relational_dynamics',    'context.relationship',       'move',   'coded',      'EDM vocab relationship/v1; Fiske as companion code'),
 ('constellation.temporal_context',       'context.life_stage',         'move',   'coded',      'Conway lifetime period'),
 ('constellation.memory_type',            'salience.memory_type',       'move',   'coded',      'Pillemer momentous-event types as codes'),
 ('constellation.media_format',           None,                         'cut',    None,         'duplicates meta.source_type; text preserved in extensions'),
 ('constellation.narrative_archetype',    None,                         'cut',    None,         'replaced by narrative.self_position (stated-only free text); enum value preserved in extensions, never copied into self_position'),
 ('constellation.symbolic_anchor',        'salience.tether',            'merge',  'object',     'tether.referent'),
 ('constellation.relational_perspective', 'context.scope',              'move',   'coded',      'Bronfenbrenner nested systems'),
 ('constellation.temporal_rhythm',        'emotion.temporal_profile',   'rename', 'coded',      'EmotionML trace / Scherer suddenness; EDM-specific shapes kept'),
 ('constellation.identity_thread',        'narrative.identity_link',    'rename', 'text',       'Conway self-memory system'),
 ('constellation.expressed_insight',      'narrative.meaning',          'rename', 'text',       'McAdams meaning-making'),
 ('constellation.transformational_pivot', 'narrative.turning_point',    'rename', 'bool',       'McAdams / Pillemer turning point'),
 ('constellation.somatic_signature',      'emotion.bodily_sensation',   'rename', 'text',       'MFOEM:000003 physiological process involved in an emotion'),
 ('constellation.arc_type',               'narrative.arc',              'move',   'coded_list', 'Booker / Campbell / McAdams'),
 # milky_way -> context / narrative
 ('milky_way.event_type',         'context.event',              'rename', 'text',   'Singer & Blagov content category as companion (context.event_category)'),
 ('milky_way.location_context',   'context.place',              'rename', 'text',   'Tulving episodic where'),
 ('milky_way.associated_people',  'context.people',             'rename', 'list',   ''),
 ('milky_way.visibility_context', None,                         'cut',    None,     'governance; duplicates meta.visibility; text preserved in extensions'),
 ('milky_way.tone_shift',         'narrative.valence_shift',    'rename', 'text',   'McAdams redemption / contamination'),
 # gravity -> emotion / salience
 ('gravity.emotional_weight',     'emotion.intensity',          'move',   'dimension', 'EmotionML intensity-dimension; numeric value carried as-is'),
 ('gravity.emotional_density',    None,                         'cut',    None,        'no framework construct; text preserved in extensions'),
 ('gravity.valence',              'emotion.valence',            'move',   'dimension', 'MFOEM:000207/000208; EmotionML fsre-dimensions#valence'),
 ('gravity.viscosity',            'salience.persistence',       'merge',  'object',    'persistence.text'),
 ('gravity.gravity_type',         'salience.tether',            'merge',  'object',    'tether.stake (Lazarus ego-involvement)'),
 ('gravity.tether_type',          'salience.tether',            'rename', 'object',    'tether.type (EDM vocab tether/v1; OCC branches)'),
 ('gravity.recall_triggers',      'salience.retrieval_cues',    'rename', 'list',      'Tulving; Conway sensory-perceptual cue'),
 ('gravity.retrieval_keys',       'salience.retrieval_cues',    'merge',  'list',      'appended to retrieval_cues'),
 ('gravity.nearby_themes',        'salience.themes',            'rename', 'list',      'Conway thematic linkage'),
 ('gravity.recurrence_pattern',   'salience.recurrence',        'rename', 'coded',     'Singer & Blagov specificity'),
 ('gravity.strength_score',       'salience.linkage_strength',  'rename', 'number',    'SDM criterion: linked to similar memories'),
 ('gravity.temporal_decay',       'salience.persistence',       'merge',  'object',    'persistence.decay'),
 ('gravity.resilience_markers',   'salience.resilience',        'rename', 'list',      'Lazarus positive reappraisal; Bar-On optimism'),
 ('gravity.adaptation_trajectory','salience.trajectory',        'rename', 'coded',     'McAdams redemption / contamination'),
 # impulse -> motivation / emotion.appraisal / context / trait
 ('impulse.primary_energy',       None,                         'cut',    None,     'duplicates emotion.primary; text preserved in extensions'),
 ('impulse.drive_state',          'motivation.action_tendency', 'rename', 'coded',  'Frijda action tendency (EmotionML frijda-action-tendencies)'),
 ('impulse.motivational_orientation','motivation.need',         'rename', 'coded',  'SDT basic psychological needs'),
 ('impulse.temporal_focus',       'motivation.temporal_focus',  'rename', 'coded',  'Tulving chronesthesia'),
 ('impulse.directionality',       'context.scope',              'merge',  'object', 'scope.direction'),
 ('impulse.social_visibility',    None,                         'cut',    None,     'duplicates context.scope and meta.visibility; text preserved in extensions'),
 ('impulse.urgency',              'emotion.appraisal.urgency',  'move',   'dimension', 'EmotionML ema-appraisals#urgency; MFOEM:000089/000090'),
 ('impulse.risk_posture',         'motivation.risk_posture',    'rename', 'coded',  'Lazarus threat / challenge'),
 ('impulse.agency_level',         'emotion.appraisal.control',  'move',   'dimension', 'EmotionML scherer-appraisals#control; MFOEM:000110/000116'),
 ('impulse.regulation_state',     'trait.regulation_state',     'trait',  'coded',  'Gross; person-level reading (theoretical-conflicts section 5) -> opt-in trait profile'),
 ('impulse.attachment_style',     'trait.attachment_style',     'trait',  'coded',  'Ainsworth / Main; person-level reading (theoretical-conflicts section 5) -> opt-in trait profile'),
 ('impulse.coping_style',         'motivation.coping',          'rename', 'coded',  'Lazarus & Folkman Ways of Coping; Gross family as second coding'),
]
NEW_FIELDS = [
 ('narrative.self_position',        'text',   "stated-only: the subject's expressed lens on themselves in the story; codes to McAdams imago (open) and agency/communion; Hermans I-positions"),
 ('emotion.kind',                   'coded',  'MFOEM:000001 emotion process | MFOEM:000193 mood process | MFOEM:000006 subjective affective feeling | MFOEM:000199 emotion disposition'),
 ('emotion.arousal',                'dimension', 'Russell; PAD; GRID; EmotionML pad-dimensions#arousal'),
 ('emotion.appraisal.attribution',  'coded',  'Scherer agent-self / agent-other / agent-nature; MFOEM:000076 / 000078 / 000077'),
 ('context.event_category',         'coded',  'Singer & Blagov / Thorne & McLean content categories'),
 ('context.relationship_model',     'coded',  'Fiske relational models'),
 ('salience.function',              'coded_list', 'Pillemer / Bluck memory functions: directive, self, social'),
 ('telemetry.field_confidence',     'object', 'EmotionML confidence attribute, per field path (infrastructure, not an affective field)'),
]
TRAIT_FIELDS = ['trait.attachment_style', 'trait.regulation_state']

# v0.9 affective layout in display order (trait and telemetry excluded)
LAYOUT_ORDER = {
 'narrative': ['subject','trigger','harm','drive','integration','summary','meaning','identity_link','turning_point','arc','valence_shift','self_position'],
 'emotion':   ['primary','secondary','kind','valence','arousal','intensity','meta','bodily_sensation','temporal_profile','appraisal.urgency','appraisal.control','appraisal.attribution'],
 'context':   ['event','event_category','place','people','relationship','relationship_model','life_stage','scope'],
 'salience':  ['memory_type','tether','retrieval_cues','themes','recurrence','persistence','linkage_strength','function','resilience','trajectory'],
 'motivation':['action_tendency','need','temporal_focus','risk_posture','coping'],
}
AFFECTIVE_COUNT = sum(len(v) for v in LAYOUT_ORDER.values())
ALL_09 = [f'{d}.{f}' for d, fs in LAYOUT_ORDER.items() for f in fs]

# Vocabularies born in v0.9 (the six new coded fields); inherited vocabularies come from fields.json below.
NEW_VOCAB = {
 'kind': ['emotion', 'mood', 'feeling', 'disposition'],
 'arousal': ['low', 'medium', 'high'],
 'attribution': ['self', 'other', 'chance'],
 'event_category': ['relationships', 'life_threatening_events', 'recreation_exploration', 'achievement_mastery', 'guilt_shame', 'drug_alcohol_tobacco_use', 'not_classifiable'],
 'relationship_model': ['communal_sharing', 'authority_ranking', 'equality_matching', 'market_pricing', 'null_relation'],
 'function': ['directive', 'self', 'social'],
}

# ---------------------------------------------------------------------------
# 2. Deprecated canonical values: still accepted as text, coded to the canonical value or marked deprecated. No text changes.
# ---------------------------------------------------------------------------
DEPRECATED_VALUES = [
 ('context.relationship', 'friend',          'friendship',          'duplicate'),
 ('context.relationship', 'couple',          'romantic_partnership','duplicate'),
 ('context.relationship', 'grief',           None,                  'an emotion, not a relational configuration'),
 ('context.relationship', 'self_reflection', None,                  'a narrative mode, not a relational configuration'),
 ('salience.memory_type', 'legacy_artifact', None,                  'an object tether, not a memory type (coded tether/v1#object, related)'),
 ('salience.persistence', 'fluid',           'transient',           'nominal value inside an ordinal scale'),
 ('salience.recurrence',  'emerging',        None,                  'not a recurrence structure'),
 ('salience.trajectory',  'emerging',        None,                  'not a trajectory direction'),
 ('emotion.temporal_profile', 'looping',     'recurring',           'overlaps recurring'),
 ('emotion.temporal_profile', 'cyclic',      'recurring',           'overlaps recurring / salience.recurrence=cyclical'),
]

# ---------------------------------------------------------------------------
# 3. Code tables used by the migration (deterministic, taken from the crosswalk; relation given where not exact)
# ---------------------------------------------------------------------------
def edm(field, value, relation='exact'):
    return {'system': VOCAB.format(field=field), 'version': '1', 'code': value, 'display': value, 'relation': relation}
def mf(label, relation='exact'):
    return {'system': MFOEM_SYS, 'version': MFOEM_VER, 'code': MF[label], 'display': label, 'relation': relation}
def eml(voc, item, relation='exact'):
    return {'system': EML.format(voc=voc), 'version': EML_VER, 'code': item, 'display': item, 'relation': relation}
def xref(fw, code, display, relation='exact'):
    return {'system': XREF.format(fw=fw), 'code': code, 'display': display, 'relation': relation}

PRIMARY_CODES = {
 'joy': [mf('joy'), eml('occ-categories', 'joy')], 'sadness': [mf('sadness'), eml('fsre-categories', 'sadness')],
 'fear': [mf('fear'), eml('big6', 'fear')], 'anger': [mf('anger'), eml('big6', 'anger')],
 'wonder': [xref('cowen_keltner', 'awe', 'awe', 'related')], 'peace': [mf('serenity')],
 'tenderness': [mf('love', 'related'), mf('compassion', 'related')], 'reverence': [xref('cowen_keltner', 'awe', 'awe', 'related')],
 'pride': [mf('pride'), eml('occ-categories', 'pride')], 'anxiety': [mf('anxiety'), eml('fsre-categories', 'anxiety')],
 'gratitude': [eml('occ-categories', 'gratitude')], 'longing': [xref('cowen_keltner', 'nostalgia', 'nostalgia', 'related')],
 'hope': [mf('hope'), eml('occ-categories', 'hope')], 'shame': [mf('shame'), eml('occ-categories', 'shame')],
 'disappointment': [mf('disappointment'), eml('occ-categories', 'disappointment')], 'relief': [eml('occ-categories', 'relief')],
 'frustration': [xref('russell', 'frustrated', 'frustrated', 'related')],
}
VALENCE_CODES = {'positive': [mf('positive valence')], 'negative': [mf('negative valence')], 'mixed': [xref('wordnet_affect', 'ambiguous', 'ambiguous')]}
URGENCY_CODES = {'calm': [mf('appraisal as not urgent response', 'related')], 'elevated': [], 'pressing': [mf('appraisal as urgent response', 'related')], 'acute': [mf('appraisal as urgent response', 'related')]}
CONTROL_CODES = {'low': [mf('feeling out of control', 'related')], 'medium': [], 'high': [mf('feeling in control', 'related')]}
NEED_CODES = {'belonging': [xref('sdt', 'relatedness', 'relatedness')], 'mastery': [xref('sdt', 'competence', 'competence')], 'autonomy': [xref('sdt', 'autonomy', 'autonomy')], 'safety': [], 'meaning': [], 'authenticity': [xref('sdt', 'autonomy', 'autonomy', 'related')]}
TENDENCY_CODES = {'explore': [eml('frijda-action-tendencies', 'attending')], 'approach': [eml('frijda-action-tendencies', 'approach')], 'avoid': [eml('frijda-action-tendencies', 'avoidance')],
 'share': [eml('frijda-action-tendencies', 'being-with')], 'confront': [eml('frijda-action-tendencies', 'agonistic')], 'protect': [eml('frijda-action-tendencies', 'dominating')],
 'repair': [], 'persevere': [], 'process': []}
COPING_CODES = {'reframe_meaning': [xref('lazarus', 'positive_reappraisal', 'Positive Reappraisal'), xref('gross', 'cognitive_change', 'cognitive change')],
 'seek_support': [xref('lazarus', 'seeking_social_support', 'Seeking Social Support')], 'distract': [xref('lazarus', 'escape_avoidance', 'Escape-Avoidance', 'related'), xref('gross', 'attentional_deployment', 'attentional deployment')],
 'confront': [xref('lazarus', 'confrontive_coping', 'Confrontive Coping')], 'detach': [xref('lazarus', 'distancing', 'Distancing')], 'ritualize': [], 'process': []}
ATTACH_CODES = {'secure': [xref('ainsworth', 'B', 'B (secure)')], 'anxious': [xref('ainsworth', 'C', 'C (insecure-ambivalent/resistant)')], 'avoidant': [xref('ainsworth', 'A', 'A (insecure-avoidant)')], 'disorganized': [xref('ainsworth', 'D', 'D (disorganized/disoriented)')]}
MEMORY_CODES = {'formative_experience': [xref('pillemer', 'originating_events', 'originating events')], 'milestone': [xref('pillemer', 'turning_points', 'turning points', 'related')], 'fleeting_moment': [], 'reflection': [], 'legacy_artifact': [edm('tether', 'object', 'related')]}
PROFILE_CODES = {'sudden': [eml('scherer-appraisals', 'suddenness'), mf('appraisal as sudden')]}
PERSISTENCE_RECODE = {'low': 'transient', 'medium': 'short', 'high': 'enduring', 'enduring': 'chronic', 'fluid': 'transient'}
DECAY_RECODE = {'fast': 'transient', 'moderate': 'short', 'slow': 'enduring'}
TETHER_CODES = {'person': [xref('occ', 'agents', 'actions of agents')], 'event': [xref('occ', 'events', 'consequences of events')], 'object': [xref('occ', 'objects', 'aspects of objects')]}
ARC_CODES = {'overcoming': [xref('booker', 'overcoming_the_monster', 'Overcoming the Monster')], 'transformation': [xref('booker', 'rebirth', 'Rebirth')], 'loss': [xref('booker', 'tragedy', 'Tragedy')],
 'connection': [xref('mcadams', 'communion', 'communion')], 'bond': [xref('mcadams', 'communion', 'communion')], 'liberation': [xref('campbell', 'freedom_to_live', 'Freedom to Live')],
 'threshold': [xref('campbell', 'crossing_of_the_first_threshold', 'The Crossing of the First Threshold')], 'grief': [mf('grief')], 'gratitude': [eml('occ-categories', 'gratitude')]}

FIELDS_083 = json.load(open(os.path.join(DISC, 'fields.json'), encoding='utf-8'))['fields']
CANONICAL = {  # v0.9 vocabulary -> canonical values inherited from v0.8.3 (an EDM code is minted only for these; free text gets no EDM code)
 'emotion': set(), 'arc': set(), 'relationship': set(), 'life_stage': set(), 'memory_type': set(), 'scope': set(), 'temporal_profile': set(),
 'valence': set(), 'persistence': set(), 'tether': set(), 'recurrence': set(), 'trajectory': set(), 'action_tendency': set(), 'need': set(),
 'temporal_focus': set(), 'urgency': set(), 'risk_posture': set(), 'control': set(), 'regulation_state': set(), 'attachment_style': set(), 'coping': set(),
}
_SRC = {'emotion': ['constellation.emotion_primary'], 'arc': ['constellation.arc_type', 'constellation.narrative_arc'], 'relationship': ['constellation.relational_dynamics'],
 'life_stage': ['constellation.temporal_context'], 'memory_type': ['constellation.memory_type'], 'scope': ['constellation.relational_perspective'],
 'temporal_profile': ['constellation.temporal_rhythm'], 'valence': ['gravity.valence'], 'persistence': ['gravity.viscosity'], 'tether': ['gravity.tether_type'],
 'recurrence': ['gravity.recurrence_pattern'], 'trajectory': ['gravity.adaptation_trajectory'], 'action_tendency': ['impulse.drive_state'], 'need': ['impulse.motivational_orientation'],
 'temporal_focus': ['impulse.temporal_focus'], 'urgency': ['impulse.urgency'], 'risk_posture': ['impulse.risk_posture'], 'control': ['impulse.agency_level'],
 'regulation_state': ['impulse.regulation_state'], 'attachment_style': ['impulse.attachment_style'], 'coping': ['impulse.coping_style']}
for _f, _paths in _SRC.items():
    for _p in _paths:
        CANONICAL[_f] |= set((next(x for x in FIELDS_083 if x['path'] == _p)['canonical_values']) or [])
CANONICAL['persistence'] |= {'transient', 'short', 'enduring', 'chronic'}
for _k, _vals in NEW_VOCAB.items(): CANONICAL[_k] = set(_vals)

# ---------------------------------------------------------------------------
# 3a. Field text. v0.8.3 description / x_constraints are read verbatim from fields.json (generated from schema/fragments);
#     DESC holds the v0.9 description and x_constraints per v0.9 path. Single source for draft_schema_build.py and for the
#     crosswalk record, which preserves both texts side by side (ruling 2026-10-18, step 2).
# ---------------------------------------------------------------------------
D083 = {f['path']: f for f in FIELDS_083}
DEP = {}
for f, v, to, why in DEPRECATED_VALUES: DEP.setdefault(f, []).append({'value': v, 'replaced_by': to, 'reason': why})

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
 'context.event_category': ('Coded companion to context.event: the content category of the event as the subject describes it.', 'Singer & Blagov / Thorne & McLean categories: ' + ', '.join(NEW_VOCAB['event_category']) + ' (labels knowledge-reconstructed; REPORT.md section 9)'),
 'context.place': (desc_of('milky_way.location_context'), D083['milky_way.location_context']['constraints']),
 'context.people': (desc_of('milky_way.associated_people'), D083['milky_way.associated_people']['constraints']),
 'context.relationship': (desc_of('constellation.relational_dynamics'), 'Canonical: ' + ', '.join(D083['constellation.relational_dynamics']['canonical_values']) + '. friend, couple, grief, self_reflection are deprecated. Free text accepted.'),
 'context.relationship_model': ("Coded companion to context.relationship: the relational model the subject's account of the relationship instantiates (Fiske).", ', '.join(NEW_VOCAB['relationship_model'])),
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

# ---------------------------------------------------------------------------
# 3c. Dispositions (ruling 2026-10-18, step 2): one per v0.8.3 field and one per canonical value. scripts/crosswalk_audit.py
#     fails if any is missing. Field rule: cut -> cut-to-extensions; trait -> moved-to-trait; a target with more than one
#     source -> merged; enum/number -> dimension -> reshaped; otherwise carried when the field name is unchanged (domain
#     rename or move only) and renamed when it changes. The uniform {text, codings} wrapping of coded fields is recorded
#     per row as shape_from / shape_to, not as a disposition. Value rule: value words never change (proposal section 4 rule 2);
#     a value is carried (with its EDM code), carried (deprecated), cut-to-extensions with its field, or moved-to-trait.
# ---------------------------------------------------------------------------
EXAMPLE_RE = re.compile(r'"([^"]+)"')
CORE_SLOTS = ['core.anchor', 'core.spark', 'core.wound', 'core.fuel', 'core.bridge', 'core.echo']
_TARGET_SOURCES = Counter(n for _, n, a, _, _ in FIELD_MAP if n and a != 'trait')
_VOCAB_OF_083 = {p: v for v, ps in _SRC.items() for p in ps}
_DEP = {(f, v): (to, why) for f, v, to, why in DEPRECATED_VALUES}
_VALUE_TARGET = {  # where a carried value lives when the v0.9 target is an object or a list
 'gravity.viscosity': 'salience.persistence.text', 'gravity.temporal_decay': 'salience.persistence.decay',
 'constellation.relational_perspective': 'context.scope.text', 'impulse.directionality': 'context.scope.direction',
 'gravity.tether_type': 'salience.tether.type.text', 'constellation.narrative_arc': 'narrative.arc[].text', 'constellation.arc_type': 'narrative.arc[].text',
 'gravity.valence': 'emotion.valence.text', 'impulse.urgency': 'emotion.appraisal.urgency.text', 'impulse.agency_level': 'emotion.appraisal.control.text',
}
_ARC_SHARED = set(D083['constellation.arc_type']['canonical_values']) & set(D083['constellation.narrative_arc']['canonical_values'])

def examples_of(constraints):
    return EXAMPLE_RE.findall(constraints or '') if 'e.g.' in (constraints or '') else []

def field_disposition(old, new, action, shape):
    if action == 'cut': return 'cut-to-extensions'
    if action == 'trait': return 'moved-to-trait'
    if action == 'merge' or _TARGET_SOURCES[new] > 1: return 'merged'
    if shape == 'dimension': return 'reshaped'
    return 'carried' if old.split('.')[-1] == new.split('.')[-1] else 'renamed'

def value_dispositions(old, new, action):
    f = D083[old]
    if f['vocabulary'] not in ('closed_enum', 'canonical_open'): return []
    rows = []
    for v in f['canonical_values']:
        if action == 'cut':
            rows.append({'value': v, 'disposition': 'cut-to-extensions', 'to': 'extensions.' + LEGACY_EXT + '.v0_8_3_cut_fields["' + old + '"]', 'text_change': False})
            continue
        vocab = _VOCAB_OF_083.get(old)
        row = {'value': v, 'disposition': 'moved-to-trait' if action == 'trait' else 'carried', 'to': _VALUE_TARGET.get(old, new + '.text'),
               'edm_code': (VOCAB.format(field=vocab) + '#' + v) if vocab else None, 'text_change': False}
        dep = _DEP.get((new, v))
        if dep:
            row['disposition'] = 'carried (deprecated)'; row['deprecated'] = {'coded_to': dep[0], 'reason': dep[1]}
        if vocab is None: row['note'] = 'plain string sub-field; no EDM vocabulary minted'
        if old in ('constellation.narrative_arc', 'constellation.arc_type') and v in _ARC_SHARED: row['note'] = 'value present in both arc_type and narrative_arc; one arc/v1 code'
        rows.append(row)
    return rows

def profiles_of_09(path):
    if path.startswith('trait.'): return ['opt-in (partner manifest)']
    return [p for p, fs in PROFILES_09.items() if path in fs]

def field_rows():
    rows = []
    for old, new, action, shape, note in FIELD_MAP:
        f = D083[old]
        row = {'from': old, 'to': new, 'disposition': field_disposition(old, new, action, shape), 'action': action,
               'shape_from': f['vocabulary'], 'shape_to': shape, 'shape': shape, 'note': note,
               'v083': {'description': f['description'], 'constraints': f['constraints'], 'examples': examples_of(f['constraints']),
                        'canonical_values': f['canonical_values'] if f['vocabulary'] in ('closed_enum', 'canonical_open') else None,
                        'profiles': f['profiles']}}
        if action == 'cut':
            row['v09'] = {'description': None, 'preserved_at': 'extensions.' + LEGACY_EXT + '.v0_8_3_cut_fields["' + old + '"]', 'text_change': False}
        else:
            d, c = DESC[new]
            row['v09'] = {'description': d, 'constraints': c, 'profiles': profiles_of_09(new)}
        if old in CORE_SLOTS:
            row['run2_arm_a'] = {'name': old.split('.')[1], 'description': f['description'], 'constraints': f['constraints'],
                                 'examples': examples_of(f['constraints']), 'shape': 'string (single value), as in v0.8.3',
                                 'note': 'verbatim v0.8.3 field text for experiment-plan-run2.md Arm A; x_status pending run 2 (prompt test), ruling R2/R3 2026-10-18'}
        row['values'] = value_dispositions(old, new, action)
        rows.append(row)
    return rows

def new_value_rows():
    rows = []
    for vocab, vals in NEW_VOCAB.items():
        for v in vals: rows.append({'vocabulary': vocab, 'value': v, 'disposition': 'added', 'edm_code': VOCAB.format(field=vocab) + '#' + v})
    for v in ('transient', 'short', 'enduring', 'chronic'):
        rows.append({'vocabulary': 'persistence', 'value': v, 'disposition': 'added', 'edm_code': VOCAB.format(field='persistence') + '#' + v, 'note': 'code only, reached from viscosity / temporal_decay by the fixed recode table; never written into text by migration'})
    return rows

CANONICAL_VALUES_083 = sum(len(f['canonical_values']) for f in FIELDS_083 if f['vocabulary'] in ('closed_enum', 'canonical_open'))

# ---------------------------------------------------------------------------
# 3b. Profile manifests for the v0.9 draft. Essential is fixed by direction (7 narrative + 4 emotion + salience.retrieval_cues,
#     ruling 2026-10-17 so that core.echo survives an Essential migration without the legacy extension); Extended and Full
#     are derived: a carried field is in a profile when any of its v0.8.3 sources was; the six new coded fields are
#     Full-only; self_position is Essential. trait.* belongs to no canonical profile (opt-in via partner manifest).
# ---------------------------------------------------------------------------
ESSENTIAL_09 = ['narrative.subject', 'narrative.trigger', 'narrative.harm', 'narrative.drive', 'narrative.integration', 'narrative.arc',
                'narrative.self_position', 'emotion.primary', 'emotion.secondary', 'emotion.valence', 'emotion.intensity',
                'salience.retrieval_cues']
_P083 = {x['path']: set(x['profiles']) for x in FIELDS_083}
def _derived(profile):
    keep = set(ESSENTIAL_09)
    for old, new, action, shape, note in FIELD_MAP:
        if new and action != 'trait' and profile in _P083[old]: keep.add(new)
    return [p for p in ALL_09 if p in keep]
PROFILES_09 = {'essential': [p for p in ALL_09 if p in set(ESSENTIAL_09)], 'extended': _derived('extended'), 'full': list(ALL_09)}
PARTNER_BASE = {'partner:com.deepadata.journaling.v1': 'extended', 'partner:com.deepadata.therapy.v1': 'full',
                'partner:com.deepadata.companion.v1': 'extended', 'partner:com.deepadata.wiki.v1': 'extended'}
TRAIT_OPT_IN = {'partner:com.deepadata.therapy.v1'}  # discovery assumption for the draft manifests
def profile_fields(profile):
    return PROFILES_09[PARTNER_BASE.get(profile, profile)]

def coded(field, value, extra=None):
    if value is None: return {'text': None, 'codings': []}
    codings = ([edm(field, value)] if value in CANONICAL.get(field, set()) else []) + list((extra or {}).get(value, []))
    return {'text': value, 'codings': codings}
def coded_list(field, values, extra=None):
    return [coded(field, v, extra) for v in (values or [])]
def dimension(text, value, codings):
    return {'text': text, 'value': value, 'codings': codings}

# ---------------------------------------------------------------------------
# 4. Migration (v0.8.3 artifact -> v0.9 draft layout). Never infers: new fields are null; numeric values are copied, never derived.
# ---------------------------------------------------------------------------
def migrate(a, profile=None):
    """profile=None gives the profile-agnostic relayout (every v0.9 field present, nulls included). With a profile
    (canonical or partner id) populated fields outside its manifest, and trait.* without opt-in, move to the legacy extension."""
    g = lambda d, k: (a.get(d) or {}).get(k)
    legacy = {}
    for old, new, action, shape, note in FIELD_MAP:
        if action == 'cut':
            d, k = old.split('.')
            if g(d, k) is not None: legacy[old] = g(d, k)
    out = {}
    out['meta'] = dict(a.get('meta') or {}); out['meta']['version'] = '0.9.0-draft'
    out['narrative'] = {
        'subject': g('core', 'anchor'), 'trigger': g('core', 'spark'), 'harm': g('core', 'wound'), 'drive': g('core', 'fuel'),
        'integration': g('core', 'bridge'), 'summary': g('core', 'narrative'), 'meaning': g('constellation', 'expressed_insight'),
        'identity_link': g('constellation', 'identity_thread'), 'turning_point': g('constellation', 'transformational_pivot'),
        'arc': coded_list('arc', [v for v in (g('constellation', 'narrative_arc'), g('constellation', 'arc_type')) if v], ARC_CODES),
        'valence_shift': g('milky_way', 'tone_shift'),
        'self_position': None,  # stated-only; never derived from narrative_archetype
    }
    secondary = coded_list('emotion', g('constellation', 'emotion_subtone'), PRIMARY_CODES)
    if g('constellation', 'higher_order_emotion'): secondary.append({'text': g('constellation', 'higher_order_emotion'), 'codings': []})
    val = g('gravity', 'valence'); urg = g('impulse', 'urgency'); ctl = g('impulse', 'agency_level'); w = g('gravity', 'emotional_weight')
    out['emotion'] = {
        'primary': coded('emotion', g('constellation', 'emotion_primary'), PRIMARY_CODES),
        'secondary': secondary,
        'kind': {'text': None, 'codings': []},
        'valence': dimension(val, None, ([edm('valence', val)] + VALENCE_CODES.get(val, [])) if val else []),
        'arousal': {'text': None, 'value': None, 'codings': []},
        'intensity': dimension(None, w, [eml('intensity-dimension', 'intensity')] if w is not None else []),
        'meta': g('constellation', 'meta_emotional_state'),
        'bodily_sensation': g('constellation', 'somatic_signature'),
        'temporal_profile': coded('temporal_profile', g('constellation', 'temporal_rhythm'), PROFILE_CODES),
        'appraisal': {
            'urgency': dimension(urg, None, ([edm('urgency', urg), eml('ema-appraisals', 'urgency')] + URGENCY_CODES.get(urg, [])) if urg else []),
            'control': dimension(ctl, None, ([edm('control', ctl), eml('scherer-appraisals', 'control')] + CONTROL_CODES.get(ctl, [])) if ctl else []),
            'attribution': {'text': None, 'codings': []},
        },
    }
    persp = g('constellation', 'relational_perspective')
    out['context'] = {
        'event': g('milky_way', 'event_type'), 'event_category': {'text': None, 'codings': []},
        'place': g('milky_way', 'location_context'), 'people': g('milky_way', 'associated_people'),
        'relationship': coded('relationship', g('constellation', 'relational_dynamics')),
        'relationship_model': {'text': None, 'codings': []},
        'life_stage': coded('life_stage', g('constellation', 'temporal_context')),
        'scope': {'text': persp, 'direction': g('impulse', 'directionality'), 'codings': [edm('scope', persp)] if persp else []},
    }
    cues = ([g('core', 'echo')] if g('core', 'echo') else []) + (g('gravity', 'recall_triggers') or []) + (g('gravity', 'retrieval_keys') or [])
    visc, decay = g('gravity', 'viscosity'), g('gravity', 'temporal_decay')
    recode = PERSISTENCE_RECODE.get(visc) or DECAY_RECODE.get(decay)
    out['salience'] = {
        'memory_type': coded('memory_type', g('constellation', 'memory_type'), MEMORY_CODES),
        'tether': {'type': coded('tether', g('gravity', 'tether_type'), TETHER_CODES), 'referent': g('constellation', 'symbolic_anchor'), 'stake': g('gravity', 'gravity_type')},
        'retrieval_cues': cues, 'themes': g('gravity', 'nearby_themes'),
        'recurrence': coded('recurrence', g('gravity', 'recurrence_pattern')),
        'persistence': {'text': visc, 'decay': decay, 'codings': [edm('persistence', recode)] if recode else []},
        'linkage_strength': g('gravity', 'strength_score'),
        'function': [], 'resilience': g('gravity', 'resilience_markers'),
        'trajectory': coded('trajectory', g('gravity', 'adaptation_trajectory')),
    }
    out['motivation'] = {
        'action_tendency': coded('action_tendency', g('impulse', 'drive_state'), TENDENCY_CODES),
        'need': coded('need', g('impulse', 'motivational_orientation'), NEED_CODES),
        'temporal_focus': coded('temporal_focus', g('impulse', 'temporal_focus')),
        'risk_posture': coded('risk_posture', g('impulse', 'risk_posture')),
        'coping': coded('coping', g('impulse', 'coping_style'), COPING_CODES),
    }
    if g('impulse', 'attachment_style') or g('impulse', 'regulation_state'):
        out['trait'] = {'attachment_style': coded('attachment_style', g('impulse', 'attachment_style'), ATTACH_CODES),
                        'regulation_state': coded('regulation_state', g('impulse', 'regulation_state'))}
    for d in ('governance', 'telemetry', 'system', 'crosswalks'):
        if d in a: out[d] = a[d]
    out.setdefault('telemetry', {})['field_confidence'] = {}
    ext = dict(a.get('extensions') or {})
    if legacy: ext[LEGACY_EXT] = {'v0_8_3_cut_fields': legacy}
    if ext: out['extensions'] = ext
    if profile: prune_to_profile(out, profile)
    return out

def is_empty(v):
    if v is None: return True
    if isinstance(v, list): return all(is_empty(x) for x in v)
    if isinstance(v, dict): return all(is_empty(x) for k, x in v.items() if k != 'codings')
    return False

def prune_to_profile(out, profile):
    """Drop v0.9 fields outside the profile manifest; populated ones are preserved verbatim in the legacy extension."""
    allowed = set(profile_fields(profile)); moved = {}
    for dom in ('narrative', 'emotion', 'context', 'salience', 'motivation', 'trait'):
        if dom not in out: continue
        for k in list(out[dom].keys()):
            path = f'{dom}.{k}'
            if dom == 'trait': keep = profile in TRAIT_OPT_IN
            elif k == 'appraisal': keep = any(p.startswith('emotion.appraisal.') for p in allowed)
            else: keep = path in allowed
            if keep: continue
            v = out[dom].pop(k)
            if not is_empty(v): moved[path] = v
        if not out[dom]: del out[dom]
    if moved:
        out.setdefault('extensions', {}).setdefault(LEGACY_EXT, {})['out_of_profile_fields'] = moved

# ---------------------------------------------------------------------------
# 5. Proof: every scalar the v0.8.3 affective domains carried is present, unchanged, in the migrated artifact (codings excluded).
# ---------------------------------------------------------------------------
def leaves(x, skip_keys=('codings',)):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in skip_keys: continue
            yield from leaves(v, skip_keys)
    elif isinstance(x, list):
        for v in x: yield from leaves(v, skip_keys)
    elif x is not None:
        yield x

def proof(old, new):
    old_domains = {d: old[d] for d in ('core', 'constellation', 'milky_way', 'gravity', 'impulse') if d in old}
    new_domains = {d: new[d] for d in ('narrative', 'emotion', 'context', 'salience', 'motivation', 'trait') if d in new}
    new_domains['extensions.' + LEGACY_EXT] = (new.get('extensions') or {}).get(LEGACY_EXT, {})
    co, cn = Counter(map(str, leaves(old_domains))), Counter(map(str, leaves(new_domains)))
    return {'old_scalar_count': sum(co.values()), 'new_scalar_count': sum(cn.values()), 'missing_in_new': sorted((co - cn).elements()), 'added_in_new': sorted((cn - co).elements()), 'text_unchanged': co == cn}

# ---------------------------------------------------------------------------
# 6. Crosswalk record (draft)
# ---------------------------------------------------------------------------
def crosswalk():
    renamed = [r for r in FIELD_MAP if r[2] in ('rename', 'move')]
    merged = [r for r in FIELD_MAP if r[2] == 'merge']
    cut = [r for r in FIELD_MAP if r[2] == 'cut']
    trait = [r for r in FIELD_MAP if r[2] == 'trait']
    n_new = len(NEW_FIELDS) - 1
    return {
     '$schema': 'http://json-schema.org/draft-07/schema#',
     'title': 'EDM v0.8.3 to v0.9.0 Migration Crosswalk (DRAFT, discovery)',
     'description': 'Draft record of the v0.9 relayout proposed in docs/discovery/ontology-crosswalk-2026-10/v0.9-proposal.md. Five affective domains are renamed (core->narrative, constellation->emotion, milky_way->context, gravity->salience, impulse->motivation); 57 affective fields become %d (%d carried by rename/move, %d merged into others, %d cut with text preserved in extensions, %d moved to an opt-in trait profile, %d new); every categorical field becomes text + codings; four fields become dimensions with a numeric value beside the ordinal text. No artifact text changes: scripts/v09_layout.py in the discovery folder proves the scalar multiset of the affective domains is identical before and after.' % (AFFECTIVE_COUNT, len(renamed), len(merged), len(cut), len(trait), n_new),
     'status': 'draft',
     'discovery_only': True,
     'version_from': '0.8.3',
     'version_to': '0.9.0',
     'release_date': None,
     'breaking_changes': True,
     'release_class': 'minor',
     'summary': {
        'domains_renamed': 5,
        'fields_added': n_new,
        'infrastructure_fields_added': 1,
        'fields_removed': len(cut),
        'fields_renamed_or_moved': len(renamed),
        'fields_merged': len(merged),
        'fields_moved_to_trait_profile': len(trait),
        'affective_field_count_before': len(FIELD_MAP),
        'affective_field_count_after': AFFECTIVE_COUNT,
        'canonical_values_before': CANONICAL_VALUES_083,
        'field_dispositions': dict(sorted(Counter(r['disposition'] for r in field_rows()).items())),
        'value_dispositions': dict(sorted(Counter(v['disposition'] for r in field_rows() for v in r['values']).items())),
        'values_deprecated': len(DEPRECATED_VALUES),
        'values_renamed': 0,
        'text_changes_required': 0,
     },
     'domain_renames': {'core': 'narrative', 'constellation': 'emotion', 'milky_way': 'context', 'gravity': 'salience', 'impulse': 'motivation'},
     'disposition_rule': 'One disposition per v0.8.3 field (carried / renamed / reshaped / merged / cut-to-extensions / moved-to-trait; new v0.9 fields are added) and one per canonical value (carried / carried (deprecated) / cut-to-extensions / moved-to-trait; new vocabulary values are added). carried = field name unchanged (domain rename or move only); renamed = field name changes; reshaped = enum or number becomes a dimension; merged = the v0.9 target has more than one v0.8.3 source. The uniform {text, codings} wrapping is recorded as shape_from / shape_to on each row. Value words never change. Audited by scripts/crosswalk_audit.py (crosswalk-audit-2026-10-18.md).',
     'field_map': field_rows(),
     'new_fields': [{'path': p, 'shape': s, 'disposition': 'added', 'note': n, 'populated_by_migration': False, 'v09': {'description': DESC[p][0], 'constraints': DESC[p][1], 'profiles': profiles_of_09(p)} if p in DESC else None} for p, s, n in NEW_FIELDS],
     'new_values': new_value_rows(),
     'trait_profile': {
        'fields': TRAIT_FIELDS,
        'rule': 'Not part of any canonical profile. A partner profile opts in by listing trait.* in included_fields. Each value is recorded only as stated for this experience and is never aggregated into a person-level classification by the artifact.',
        'migration': 'A v0.8.3 artifact carrying attachment_style or regulation_state keeps them in trait.* only when the target profile opts in; otherwise they are preserved verbatim in extensions.' + LEGACY_EXT + '.out_of_profile_fields.',
     },
     'profiles': {'essential': PROFILES_09['essential'], 'extended': PROFILES_09['extended'], 'full': PROFILES_09['full'], 'trait_opt_in_partner_profiles': sorted(TRAIT_OPT_IN),
                  'rule': 'Essential = 7 narrative + 4 emotion + salience.retrieval_cues (12; ruling 2026-10-17). A carried field is in Extended when any of its v0.8.3 sources was; the six new coded fields are Full-only. extensions is allowed in all three composites. text of coded fields is a recommended vocabulary (string; canonical list documented, not an enum); codings on the EDM vocabulary are enumerated. Draft schema: docs/discovery/ontology-crosswalk-2026-10/draft-schema/.'},
     'coding_shape': {
        'coded': {'text': 'string (the interpretation; mandatory when the field is populated)', 'codings': [{'system': 'URI', 'version': 'string', 'code': 'string', 'display': 'string', 'relation': 'exact | broader | narrower | related (default exact)'}]},
        'dimension': {'text': 'ordinal label or null', 'value': 'number or null (never derived from text by migration)', 'codings': '[...]'},
        'edm_vocabulary': VOCAB.format(field='<field>') + '#<value>',
        'xref_namespace': XREF.format(fw='<framework_id>') + '#<slug> (placeholder for frameworks that publish no concept URIs)',
     },
     'deprecated_values': [{'field': f, 'value': v, 'coded_to': to, 'reason': why, 'text_change': False} for f, v, to, why in DEPRECATED_VALUES],
     'backward_compatibility': {
        'v083_to_v090': 'Automatic. Paths change; no text changes. Cut fields are preserved verbatim under extensions.' + LEGACY_EXT + '. New fields are null until re-extracted; the migration never infers them.',
        'v090_to_v083': 'Lossy only for new fields and codings; the reverse map is field_map inverted.',
     },
     'migration_notes': {
        'automatic_upgrade': True, 'data_loss_risk': 'none (cut-field text preserved in extensions)',
        'steps': ['1. Rename domains and fields per field_map.', '2. Wrap categorical values as {text, codings} and apply codes from the vocabulary files; text is copied, never translated.', '3. Carry numeric intensity into emotion.intensity.value; leave valence/urgency/control value null.', '4. Concatenate echo + recall_triggers + retrieval_keys into salience.retrieval_cues; append higher_order_emotion to emotion.secondary; collect narrative_arc and arc_type into narrative.arc[].', '5. Move attachment_style and regulation_state to trait.* only if the target profile opts in; otherwise preserve them in extensions.', '6. Copy cut-field values into extensions.' + LEGACY_EXT + '.v0_8_3_cut_fields.', '7. Prune to the target profile manifest; any populated field outside it goes to extensions.' + LEGACY_EXT + '.out_of_profile_fields (nothing for the seven synthetic examples once Essential carries salience.retrieval_cues).', '8. Set meta.version.'],
        'reference_implementation': 'docs/discovery/ontology-crosswalk-2026-10/scripts/v09_layout.py',
     },
    }

if __name__ == '__main__':
    ex_dir, out_crosswalk, out_example = sys.argv[1:4]
    migrated_dir = sys.argv[4] if len(sys.argv) > 4 else None
    ex_path = os.path.join(ex_dir, 'example-full-profile.json')
    old = json.load(open(ex_path, encoding='utf-8'))
    new = migrate(old, 'full')
    p = proof(old, new)
    json.dump(crosswalk(), open(out_crosswalk, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump({'source': os.path.basename(os.path.normpath(ex_dir)) + '/example-full-profile.json', 'proof': p, 'migrated': new},
              open(out_example, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print('affective fields v0.9:', AFFECTIVE_COUNT, {k: len(v) for k, v in LAYOUT_ORDER.items()})
    print('profiles:', {k: len(v) for k, v in PROFILES_09.items()})
    print('proof:', json.dumps(p))
    if migrated_dir:
        os.makedirs(os.path.join(migrated_dir, 'unpruned'), exist_ok=True)
        for name in sorted(os.listdir(ex_dir)):
            if not name.endswith('.json'): continue
            src = json.load(open(os.path.join(ex_dir, name), encoding='utf-8'))
            prof = src['meta']['profile']
            mig = migrate(src, prof); pr = proof(src, mig)
            json.dump(mig, open(os.path.join(migrated_dir, name), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            json.dump(migrate(src), open(os.path.join(migrated_dir, 'unpruned', name), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            moved = sorted(((mig.get('extensions') or {}).get(LEGACY_EXT) or {}).get('out_of_profile_fields', {}).keys())
            print(f"  {name}: profile={prof} proof={'ok' if pr['text_unchanged'] else 'FAIL ' + json.dumps(pr)} out_of_profile={moved}")
