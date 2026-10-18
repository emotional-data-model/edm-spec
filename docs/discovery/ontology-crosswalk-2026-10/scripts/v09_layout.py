"""v0.9 discovery layout: the proposed field map (v0.8.3 -> v0.9.0), the draft crosswalk record,
and a migration demonstration proving that artifact text is unchanged by the relayout.

Usage:
  python -I scripts/v09_layout.py <examples-dir> <out-crosswalk.json> <out-migration-example.json> [<migrated-out-dir>]

<examples-dir> holds the seven v0.8.3 artifacts (synthetic-examples/ on this branch). The migration example is built
from example-full-profile.json; with <migrated-out-dir> every artifact in the directory is migrated, pruned to its
(base) profile's v0.9 manifest, and written there for validation against draft-schema/ (an unpruned copy goes to
<migrated-out-dir>/unpruned/ so the profile-agnostic relayout can be validated too).

Discovery only. Nothing here is normative; the crosswalk is written with status "draft".

Rulings applied here (rulings-2026-10-18.md, ruling under delegation, veto by exception): R5 (value member of valence / arousal /
urgency / control deleted), R6 (meaning interpretive-attributed), R11-R16 (core-slot text, shape, class), R17 (profiles derived from
comparability class; see section 3e; run 3 applied under R18-R28, 2026-10-18 close). `python -I scripts/v09_layout.py --membership` prints the R17 membership table.
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
#    shape : text | list | coded (text+codings) | coded_list | dimension (text+value+codings; emotion.intensity only after R5) | bool | number | object
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
 ('gravity.valence',              'emotion.valence',            'move',   'coded',     'MFOEM:000207/000208; EmotionML fsre-dimensions#valence as a coding; numeric value member removed (R5, applied 2026-10-18)'),
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
 ('impulse.urgency',              'emotion.appraisal.urgency',  'move',   'coded',     'EmotionML ema-appraisals#urgency as a coding; MFOEM:000089/000090; numeric value member removed (R5, applied 2026-10-18)'),
 ('impulse.risk_posture',         'motivation.risk_posture',    'rename', 'coded',  'Lazarus threat / challenge'),
 ('impulse.agency_level',         'emotion.appraisal.control',  'move',   'coded',     'EmotionML scherer-appraisals#control as a coding; MFOEM:000110/000116; numeric value member removed (R5, applied 2026-10-18)'),
 ('impulse.regulation_state',     'trait.regulation_state',     'trait',  'coded',  'Gross; person-level reading (theoretical-conflicts section 5) -> opt-in trait profile'),
 ('impulse.attachment_style',     'trait.attachment_style',     'trait',  'coded',  'Ainsworth / Main; person-level reading (theoretical-conflicts section 5) -> opt-in trait profile'),
 ('impulse.coping_style',         'motivation.coping',          'rename', 'coded',  'Lazarus & Folkman Ways of Coping; Gross family as second coding'),
]
NEW_FIELDS = [
 ('narrative.self_position',        'text',   "stated-only: the subject's expressed lens on themselves in the story; codes to McAdams imago (open) and agency/communion; Hermans I-positions"),
 ('emotion.kind',                   'coded',  'MFOEM:000001 emotion process | MFOEM:000193 mood process | MFOEM:000006 subjective affective feeling | MFOEM:000199 emotion disposition'),
 ('emotion.arousal',                'coded',  'Russell; PAD; GRID; EmotionML pad-dimensions#arousal as a coding; born without a numeric value member (R5, applied 2026-10-18)'),
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

# Run-2 Arm B field texts, verbatim from experiment-plan-run2.md section 4.3 (frozen b1354ee), for the slots whose ruling adopted
# Arm B (R11 harm, R12 trigger). The referent rule of that block is carried as the constraint. R13 / R14 / R15 keep the v0.8.3
# wording (Arm A) under the v0.9 name, which desc_of() already provides.
ARM_B_RULES = {
 'trigger': 'What set the feeling off? Name the moment, event or perception the text presents as starting the response it dwells on most. Not the topic of the text and not its subject; if the text states a feeling without an initiating event, null.',
 'harm': "What hurt? Name the loss, pain or vulnerability the text states, in the text's own word where it has one. A stated worry, fear, loss or vulnerability counts; one you would have to infer does not. Null if the text states none.",
}
ARM_B_CONSTRAINT = ('1-5 words, single string. Referent rule: name ONE referent that the text itself mentions, using the text\'s own noun phrase where it has one; '
                    'if several candidates qualify, choose the one the text returns to most; use the most specific noun phrase the text itself uses; '
                    'do not substitute a category the text does not use and do not add detail the text does not give. Null when no passage supports an answer; never null when one does.')
RETRIEVAL_CUES_MAX = 3  # R16

# field path -> (description, x_constraints)
DESC = {
 'narrative.subject': (desc_of('core.anchor'), D083['core.anchor']['constraints']),
 'narrative.trigger': (ARM_B_RULES['trigger'], ARM_B_CONSTRAINT + " Arm B definition adopted by R12 (2026-10-18); v0.8.3 spark read: '" + desc_of('core.spark') + "'."),
 'narrative.harm': (ARM_B_RULES['harm'], ARM_B_CONSTRAINT + " Arm B definition adopted by R11 (2026-10-18); v0.8.3 wound read: '" + desc_of('core.wound') + "'."),
 'narrative.drive': (desc_of('core.fuel'), D083['core.fuel']['constraints']),
 'narrative.integration': (desc_of('core.bridge'), D083['core.bridge']['constraints']),
 'narrative.summary': (desc_of('core.narrative'), D083['core.narrative']['constraints']),
 'narrative.meaning': ('The realization or conclusion the subject draws from the experience, as the text supports it. Interpretive, attributed: an interpretation attributable to a passage, not a quotation; null only when the text offers no basis. (R6 2026-10-18; v0.8.3: "' + desc_of('constellation.expressed_insight') + '")',
                       "Short sentence. Interpretive, attributed (R6 2026-10-18); v0.8.3 read 'Extracted, not inferred'."),
 'narrative.identity_link': (desc_of('constellation.identity_thread'), D083['constellation.identity_thread']['constraints']),
 'narrative.turning_point': (desc_of('constellation.transformational_pivot'), 'true or false; null when the subject does not say'),
 'narrative.arc': ('The story movement(s) the experience represents. A list so that a structural reading (v0.8.3 arc_type) and a trajectory reading (v0.8.3 narrative_arc) of the same memory can both be stored; order carries no meaning.', 'Each item is text + codings; EDM vocab arc/v1 unites the former arc_type and narrative_arc value sets. Free text accepted.'),
 'narrative.valence_shift': (desc_of('milky_way.tone_shift'), D083['milky_way.tone_shift']['constraints']),
 'narrative.self_position': ("The subject's own expressed lens on themselves within the story: the position they say they occupy (e.g. \"the one who holds it together\", \"the person who finally said no\"). STATED-ONLY: recorded only when the subject says it or paraphrases it unmistakably; never assigned from the plot, the emotion or an archetype catalogue.", 'Short phrase in the subject\'s own terms; NULL when not stated. Replaces narrative_archetype (the Mark & Pearson 12 are not used). Optional codings: McAdams imago (open label), agency / communion, Hermans I-position; all relation=related.'),
 'emotion.primary': (desc_of('constellation.emotion_primary'), D083['constellation.emotion_primary']['constraints']),
 'emotion.secondary': ('Secondary emotional nuances that add depth to the primary emotion, including any complex or layered state (v0.8.3 emotion_subtone + higher_order_emotion)', '0-5 items; free text; each item may carry codings with a per-coding confidence'),
 'emotion.kind': ('Whether the subject describes the affect as an episode with an object (emotion), a diffuse state without one (mood), a felt bodily quality (feeling), or a standing disposition. Stated-only; NULL when the subject does not distinguish.', 'emotion -> MFOEM:000001; mood -> MFOEM:000193; feeling -> MFOEM:000006; disposition -> MFOEM:000199'),
 'emotion.valence': (desc_of('gravity.valence'), 'text positive / negative / mixed; codings on EDM vocab valence/v1, MFOEM and EmotionML fsre-dimensions#valence. No numeric value member: removed by R5 (2026-10-18; never populated in run 1).'),
 'emotion.arousal': ('The stated activation level of the experience (keyed up vs calm), independent of valence and of intensity. Stated-only.', 'text low / medium / high; codings on EDM vocab arousal/v1 and EmotionML pad-dimensions#arousal; NULL when not expressed. No numeric value member (R5, 2026-10-18).'),
 'emotion.intensity': (desc_of('gravity.emotional_weight'), 'value in [0, 1] (v0.8.3 emotional_weight carried as-is); text is an optional ordinal label'),
 'emotion.meta': (desc_of('constellation.meta_emotional_state'), D083['constellation.meta_emotional_state']['constraints']),
 'emotion.bodily_sensation': (desc_of('constellation.somatic_signature'), D083['constellation.somatic_signature']['constraints']),
 'emotion.temporal_profile': (desc_of('constellation.temporal_rhythm'), 'Canonical: ' + ', '.join(D083['constellation.temporal_rhythm']['canonical_values']) + '. looping and cyclic are deprecated (code to recurring). Free text accepted.'),
 'emotion.appraisal.urgency': (desc_of('impulse.urgency'), 'text calm / elevated / pressing / acute; codings on EDM vocab urgency/v1, EmotionML ema-appraisals#urgency and MFOEM. No numeric value member: removed by R5 (2026-10-18; never populated in run 1).'),
 'emotion.appraisal.control': (desc_of('impulse.agency_level'), 'text low / medium / high; codings on EDM vocab control/v1, EmotionML scherer-appraisals#control and MFOEM. No numeric value member: removed by R5 (2026-10-18; never populated in run 1).'),
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
 'salience.retrieval_cues': ('What would bring this back? At most three cues the text says still resonate or would re-evoke the experience (a sensory detail, a phrase, an object), the first being the one the text returns to most. Carries v0.8.3 core.echo (first), then recall_triggers and retrieval_keys by migration. (R16 2026-10-18: short ordered list adopted; the single-string echo did no better in run 2.)', 'Short ordered list, 1-5 words per cue, at most 3 items; order carries meaning (first = the cue the text returns to most); empty list only if the text names nothing that recurs. Migration keeps the first three merged values here and preserves any further v0.8.3 values verbatim in extensions.' + LEGACY_EXT + '.retrieval_cues_overflow.'),
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
            ann = run1_for_field(new)
            if ann: row['v09']['run1_annotations'] = ann
            row['v09']['comparability'] = COMPARABILITY.get(new)
            if new in RUN2: row['v09']['run2'] = {'ruling': RUN2[new]['ruling'], 'arm_adopted': RUN2[new]['arm_adopted'], 'class': RUN2[new]['class'], 'class_basis': RUN2[new]['class_basis']}
            if new + '.value' in VALUE_REMOVED: row['v09']['value_member'] = 'removed (R5 2026-10-18; never populated in run 1); deleted from the draft schema 2026-10-18: the field is coded text + codings'; row['shape_to'] = row['shape'] = 'coded (value removed, R5)'
            elif new + '.value' in VALUE_KEPT: row['v09']['value_member'] = 'kept (R5 2026-10-18)'
        if old in CORE_SLOTS:
            row['run2_arm_a'] = {'name': old.split('.')[1], 'description': f['description'], 'constraints': f['constraints'],
                                 'examples': examples_of(f['constraints']), 'shape': 'string (single value), as in v0.8.3',
                                 'note': 'verbatim v0.8.3 field text; was Arm A of run 2 (experiment-plan-run2.md section 4.2); the slot ruling R11-R16 says which arm the v0.9 text adopts'}
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
# 3d. Evidence, embedded as literals so the draft schema build reads no experiment file.
#     RUN1_POOLED: run-1 pooled outcome per scored unit (experiments/2026-10-17/RESULTS.md section 1.1; scoring/field_table.json
#     "pooled"; thresholds frozen in experiment-plan.md section 4.1; outcome rule section 4.3).
#     RUN2: run-2 pooled outcome per core slot and prompt arm under the R9 three-voter rule (experiments/2026-10-18-run2/RESULTS.md
#     section 1; scoring/field_table.json), with the arm and the comparability class that rulings R11-R16 fixed for the slot.
#     R5 (applied 2026-10-18): the value member of valence / arousal / urgency / control is deleted from the draft; the four
#     'pending' value units stay in RUN1_POOLED as the record of why (never populated).
#     RUN3: run-3 pooled outcome per comparable-tier lead unit (experiments/2026-10-18-run3/RESULTS.md sections 1-2;
#     scoring/field_table.json; thresholds frozen in experiment-plan-run3.md section 7 at 974408e): holds of 8 under the
#     literal coverage reading (a, frozen) and under R18's reading (b, null-valued answers count as covered; decides
#     prospectively), per new arm repeat / agree / coverage / decision, the majority's text count and null share, texts the
#     judge has not reached (free text; the judge pass is incomplete: four-field group 127 of 150, summary 69 of 150), the
#     framing bound (Sonnet 47-field vs 19-field prompt) and the ruling (R19-R28). Regenerate from field_table.json when the
#     judge completes (see the close instruction in rulings-2026-10-18.md R20).
# ---------------------------------------------------------------------------
SIX_SLOTS = ['narrative.subject', 'narrative.trigger', 'narrative.harm', 'narrative.drive', 'narrative.integration', 'salience.retrieval_cues']
VALUE_REMOVED = ['emotion.valence.value', 'emotion.arousal.value', 'emotion.appraisal.urgency.value', 'emotion.appraisal.control.value']
VALUE_KEPT = ['emotion.intensity.value', 'salience.linkage_strength']
RUN1_SOURCE = 'experiments/2026-10-17/RESULTS.md section 1.1 (pooled, 150 texts, frozen thresholds of experiment-plan.md section 4.1)'
RUN2_SOURCE = 'experiments/2026-10-18-run2/RESULTS.md section 1 (pooled, 150 texts, R9 three-voter rule, thresholds frozen in experiment-plan-run2.md section 7 at b1354ee)'
RULINGS = 'docs/discovery/ontology-crosswalk-2026-10/rulings-2026-10-18.md'
VOTERS = ['claude-sonnet-5-5', 'gpt-6.1-sol', 'kimi-k2.6']
def _arm(rep, cross, cross_nn, null, outcome, two_voter):
    return {'repeat': dict(zip(VOTERS, rep)), 'cross': cross, 'cross_populated_only': cross_nn, 'null_rate': null, 'outcome': outcome, 'two_voter': two_voter}
RUN2 = {
 'narrative.harm':         {'ruling': 'R11', 'arm_adopted': 'B', 'class': 'comparable',
                            'class_basis': 'Arm B passes the frozen three-voter rule (all three voters >= 0.80, cross 0.64 >= 0.60; populated-only 0.61)',
                            'A': _arm((0.93, 0.89, 0.79), 0.66, 0.63, 0.35, 'borderline-cut', 'pass'), 'B': _arm((0.90, 0.85, 0.82), 0.64, 0.61, 0.33, 'pass', 'pass')},
 'narrative.trigger':      {'ruling': 'R12', 'arm_adopted': 'B', 'class': 'interpretive',
                            'class_basis': 'Arm B is interpretive under the frozen rule (all three voters >= 0.80, cross 0.56 < 0.60; populated-only 0.61)',
                            'A': _arm((0.93, 0.87, 0.74), 0.53, 0.57, 0.09, 'borderline-cut', 'interpretive'), 'B': _arm((0.90, 0.83, 0.80), 0.56, 0.61, 0.19, 'interpretive', 'interpretive')},
 'narrative.subject':      {'ruling': 'R13', 'arm_adopted': 'A', 'class': 'interpretive',
                            'class_basis': 'neither arm passes; Arm A text kept (Arm B selection rule lowered cross 0.53 -> 0.41); classed interpretive on the two-voter reading (Sonnet 0.91 / GPT 0.85 repeat, cross2 0.58), Kimi 0.76 the one voter short',
                            'A': _arm((0.91, 0.85, 0.76), 0.53, 0.58, 0.05, 'borderline-cut', 'interpretive'), 'B': _arm((0.94, 0.84, 0.72), 0.41, 0.42, 0.01, 'borderline-cut', 'interpretive')},
 'narrative.integration':  {'ruling': 'R14', 'arm_adopted': 'A', 'class': 'null-driven',
                            'class_basis': 'cross above the bar in both arms (0.67 / 0.62; populated-only 0.60 / 0.62) with one voter short in each (Kimi 0.75 in A, GPT 0.79 in B); null 0.48 unchanged by the Arm B null clause; the R4 null-driven annotation stays until a run passes it with all three voters',
                            'A': _arm((0.89, 0.88, 0.75), 0.67, 0.60, 0.48, 'borderline-cut', 'pass'), 'B': _arm((0.89, 0.79, 0.83), 0.62, 0.62, 0.48, 'borderline-cut', 'cut')},
 'narrative.drive':        {'ruling': 'R15', 'arm_adopted': 'A', 'class': 'interpretive',
                            'class_basis': 'not comparable under either text (cross 0.39 / 0.46); Arm A kept as the better of two failing texts; repeatable in Sonnet and GPT (0.85 / 0.86), Kimi 0.68',
                            'A': _arm((0.85, 0.86, 0.68), 0.39, 0.48, 0.27, 'borderline-cut', 'interpretive'), 'B': _arm((0.82, 0.78, 0.70), 0.46, 0.51, 0.27, 'cut', 'cut')},
 'salience.retrieval_cues': {'ruling': 'R16', 'arm_adopted': 'B', 'class': 'extractor-bound',
                            'class_basis': 'no arm and no corpus passes (cross 0.40 / 0.40); the capped list removed empty lists (null 0.31 -> 0.07) without raising agreement; Sonnet alone repeats it at 0.82-0.85',
                            'A': _arm((0.85, 0.80, 0.68), 0.40, 0.43, 0.31, 'borderline-cut', 'interpretive'), 'B': _arm((0.82, 0.77, 0.70), 0.40, 0.42, 0.07, 'cut', 'cut')},
}
RUN1_POOLED = {'narrative.subject': {'outcome': 'cut',
                       'repeat': {'claude-sonnet-5-5': 0.86, 'claude-haiku-5-5': 0.7, 'gpt-6.1-sol': 0.71, 'kimi-k2.6': 0.67},
                       'cross': 0.4,
                       'null': 0.05,
                       'flags': [],
                       'cross_populated': 0.45},
 'narrative.trigger': {'outcome': 'cut',
                       'repeat': {'claude-sonnet-5-5': 0.87, 'claude-haiku-5-5': 0.67, 'gpt-6.1-sol': 0.76, 'kimi-k2.6': 0.65},
                       'cross': 0.53,
                       'null': 0.09,
                       'flags': ['borderline'],
                       'cross_populated': 0.56},
 'narrative.harm': {'outcome': 'cut',
                    'repeat': {'claude-sonnet-5-5': 0.85, 'claude-haiku-5-5': 0.69, 'gpt-6.1-sol': 0.75, 'kimi-k2.6': 0.71},
                    'cross': 0.54,
                    'null': 0.36,
                    'flags': ['borderline'],
                    'cross_populated': 0.42},
 'narrative.drive': {'outcome': 'cut',
                     'repeat': {'claude-sonnet-5-5': 0.8, 'claude-haiku-5-5': 0.6, 'gpt-6.1-sol': 0.68, 'kimi-k2.6': 0.55},
                     'cross': 0.38,
                     'null': 0.19,
                     'flags': ['borderline'],
                     'cross_populated': 0.41},
 'narrative.integration': {'outcome': 'pass',
                           'repeat': {'claude-sonnet-5-5': 0.88, 'claude-haiku-5-5': 0.83, 'gpt-6.1-sol': 0.86, 'kimi-k2.6': 0.87},
                           'cross': 0.72,
                           'null': 0.67,
                           'flags': ['borderline', 'null-driven'],
                           'cross_populated': 0.4},
 'narrative.meaning': {'outcome': 'pass',
                       'repeat': {'claude-sonnet-5-5': 0.93, 'claude-haiku-5-5': 0.83, 'gpt-6.1-sol': 0.84, 'kimi-k2.6': 0.91},
                       'cross': 0.71,
                       'null': 0.54,
                       'flags': ['borderline'],
                       'cross_populated': 0.67},
 'narrative.identity_link': {'outcome': 'pass',
                             'repeat': {'claude-sonnet-5-5': 0.91, 'claude-haiku-5-5': 0.85, 'gpt-6.1-sol': 0.92, 'kimi-k2.6': 0.9},
                             'cross': 0.82,
                             'null': 0.72,
                             'flags': ['null-driven'],
                             'cross_populated': 0.59},
 'narrative.valence_shift': {'outcome': 'cut',
                             'repeat': {'claude-sonnet-5-5': 0.83, 'claude-haiku-5-5': 0.65, 'gpt-6.1-sol': 0.86, 'kimi-k2.6': 0.76},
                             'cross': 0.58,
                             'null': 0.45,
                             'flags': ['borderline'],
                             'cross_populated': 0.38},
 'narrative.self_position': {'outcome': 'pass',
                             'repeat': {'claude-sonnet-5-5': 0.96, 'claude-haiku-5-5': 0.9, 'gpt-6.1-sol': 0.93, 'kimi-k2.6': 0.96},
                             'cross': 0.87,
                             'null': 0.79,
                             'flags': [],
                             'cross_populated': 0.81},
 'narrative.summary': {'outcome': 'pass',
                       'repeat': {'claude-sonnet-5-5': 0.98, 'claude-haiku-5-5': 0.79, 'gpt-6.1-sol': 1.0, 'kimi-k2.6': 0.83},
                       'cross': 0.78,
                       'null': 0.04,
                       'flags': ['borderline'],
                       'cross_populated': 0.84},
 'narrative.turning_point': {'outcome': 'pass',
                             'repeat': {'claude-sonnet-5-5': 0.83, 'claude-haiku-5-5': 0.84, 'gpt-6.1-sol': 0.96, 'kimi-k2.6': 0.76},
                             'cross': 0.58,
                             'null': 0.89,
                             'flags': []},
 'narrative.arc': {'outcome': 'cut',
                   'repeat': {'claude-sonnet-5-5': 0.78, 'claude-haiku-5-5': 0.68, 'gpt-6.1-sol': 0.74, 'kimi-k2.6': 0.66},
                   'cross': 0.48,
                   'null': 0.22,
                   'flags': ['borderline']},
 'emotion.primary': {'outcome': 'pass',
                     'repeat': {'claude-sonnet-5-5': 0.86, 'claude-haiku-5-5': 0.76, 'gpt-6.1-sol': 0.84, 'kimi-k2.6': 0.78},
                     'cross': 0.57,
                     'null': 0.11,
                     'flags': []},
 'emotion.secondary': {'outcome': 'cut',
                       'repeat': {'claude-sonnet-5-5': 0.71, 'claude-haiku-5-5': 0.57, 'gpt-6.1-sol': 0.75, 'kimi-k2.6': 0.64},
                       'cross': 0.36,
                       'null': 0.2,
                       'flags': ['borderline']},
 'emotion.kind': {'outcome': 'cut',
                  'repeat': {'claude-sonnet-5-5': 1.0, 'claude-haiku-5-5': 0.61, 'gpt-6.1-sol': 0.84, 'kimi-k2.6': 0.6},
                  'cross': 0.24,
                  'null': 0.98,
                  'flags': ['sparse']},
 'emotion.valence.text': {'outcome': 'pass',
                          'repeat': {'claude-sonnet-5-5': 0.95, 'claude-haiku-5-5': 0.84, 'gpt-6.1-sol': 0.95, 'kimi-k2.6': 0.83},
                          'cross': 0.74,
                          'null': 0.11,
                          'flags': []},
 'emotion.valence.value': {'outcome': 'pending',
                           'repeat': {'claude-sonnet-5-5': None, 'claude-haiku-5-5': None, 'gpt-6.1-sol': None, 'kimi-k2.6': None},
                           'cross': None,
                           'null': 0.99,
                           'flags': ['sparse', 'value never populated']},
 'emotion.arousal.text': {'outcome': 'cut',
                          'repeat': {'claude-sonnet-5-5': 0.7, 'claude-haiku-5-5': 0.59, 'gpt-6.1-sol': 0.73, 'kimi-k2.6': 0.47},
                          'cross': 0.26,
                          'null': 0.91,
                          'flags': ['borderline', 'sparse']},
 'emotion.arousal.value': {'outcome': 'pending',
                           'repeat': {'claude-sonnet-5-5': None, 'claude-haiku-5-5': None, 'gpt-6.1-sol': None, 'kimi-k2.6': None},
                           'cross': None,
                           'null': 0.99,
                           'flags': ['sparse', 'value never populated']},
 'emotion.intensity.text': {'outcome': 'cut',
                            'repeat': {'claude-sonnet-5-5': 0.85, 'claude-haiku-5-5': 0.54, 'gpt-6.1-sol': 0.59, 'kimi-k2.6': 0.49},
                            'cross': 0.16,
                            'null': 0.33,
                            'flags': []},
 'emotion.intensity.value': {'outcome': 'pass',
                             'repeat': {'claude-sonnet-5-5': 0.98, 'claude-haiku-5-5': 0.91, 'gpt-6.1-sol': 0.0, 'kimi-k2.6': 0.98},
                             'cross': 0.77,
                             'null': 0.46,
                             'flags': []},
 'emotion.appraisal.urgency.text': {'outcome': 'cut',
                                    'repeat': {'claude-sonnet-5-5': 0.76, 'claude-haiku-5-5': 0.5, 'gpt-6.1-sol': 0.7, 'kimi-k2.6': 0.36},
                                    'cross': 0.15,
                                    'null': 0.8,
                                    'flags': ['borderline']},
 'emotion.appraisal.urgency.value': {'outcome': 'pending',
                                     'repeat': {'claude-sonnet-5-5': None, 'claude-haiku-5-5': None, 'gpt-6.1-sol': None, 'kimi-k2.6': None},
                                     'cross': None,
                                     'null': 1.0,
                                     'flags': ['sparse', 'value never populated']},
 'emotion.appraisal.control.text': {'outcome': 'cut',
                                    'repeat': {'claude-sonnet-5-5': 0.78, 'claude-haiku-5-5': 0.55, 'gpt-6.1-sol': 0.68, 'kimi-k2.6': 0.42},
                                    'cross': 0.36,
                                    'null': 0.79,
                                    'flags': ['borderline']},
 'emotion.appraisal.control.value': {'outcome': 'pending',
                                     'repeat': {'claude-sonnet-5-5': None, 'claude-haiku-5-5': None, 'gpt-6.1-sol': None, 'kimi-k2.6': None},
                                     'cross': None,
                                     'null': 1.0,
                                     'flags': ['sparse', 'value never populated']},
 'emotion.meta': {'outcome': 'cut',
                  'repeat': {'claude-sonnet-5-5': 0.87, 'claude-haiku-5-5': 0.74, 'gpt-6.1-sol': 0.91, 'kimi-k2.6': 0.72},
                  'cross': 0.65,
                  'null': 0.63,
                  'flags': ['borderline'],
                  'cross_populated': 0.34},
 'emotion.bodily_sensation': {'outcome': 'pass',
                              'repeat': {'claude-sonnet-5-5': 0.98, 'claude-haiku-5-5': 0.95, 'gpt-6.1-sol': 0.97, 'kimi-k2.6': 0.95},
                              'cross': 0.94,
                              'null': 0.79,
                              'flags': [],
                              'cross_populated': 0.84},
 'emotion.temporal_profile': {'outcome': 'interpretive',
                              'repeat': {'claude-sonnet-5-5': 0.8, 'claude-haiku-5-5': 0.67, 'gpt-6.1-sol': 0.75, 'kimi-k2.6': 0.73},
                              'cross': 0.37,
                              'null': 0.56,
                              'flags': ['borderline']},
 'emotion.appraisal.attribution': {'outcome': 'pass',
                                   'repeat': {'claude-sonnet-5-5': 0.98, 'claude-haiku-5-5': 0.8, 'gpt-6.1-sol': 0.77, 'kimi-k2.6': 0.78},
                                   'cross': 0.55,
                                   'null': 0.78,
                                   'flags': []},
 'context.event': {'outcome': 'cut',
                   'repeat': {'claude-sonnet-5-5': 0.79, 'claude-haiku-5-5': 0.65, 'gpt-6.1-sol': 0.85, 'kimi-k2.6': 0.67},
                   'cross': 0.41,
                   'null': 0.03,
                   'flags': ['borderline'],
                   'cross_populated': 0.44},
 'context.event_category': {'outcome': 'pass',
                            'repeat': {'claude-sonnet-5-5': 0.86, 'claude-haiku-5-5': 0.79, 'gpt-6.1-sol': 0.81, 'kimi-k2.6': 0.74},
                            'cross': 0.6,
                            'null': 0.05,
                            'flags': ['borderline']},
 'context.place': {'outcome': 'cut',
                   'repeat': {'claude-sonnet-5-5': 0.86, 'claude-haiku-5-5': 0.73, 'gpt-6.1-sol': 0.86, 'kimi-k2.6': 0.72},
                   'cross': 0.56,
                   'null': 0.26,
                   'flags': ['borderline'],
                   'cross_populated': 0.5},
 'context.people': {'outcome': 'cut',
                    'repeat': {'claude-sonnet-5-5': 0.82, 'claude-haiku-5-5': 0.67, 'gpt-6.1-sol': 0.87, 'kimi-k2.6': 0.79},
                    'cross': 0.55,
                    'null': 0.15,
                    'flags': ['borderline'],
                    'cross_populated': 0.52},
 'context.relationship': {'outcome': 'pass',
                          'repeat': {'claude-sonnet-5-5': 0.85, 'claude-haiku-5-5': 0.72, 'gpt-6.1-sol': 0.78, 'kimi-k2.6': 0.83},
                          'cross': 0.6,
                          'null': 0.24,
                          'flags': ['borderline']},
 'context.relationship_model': {'outcome': 'cut',
                                'repeat': {'claude-sonnet-5-5': 0.75, 'claude-haiku-5-5': 0.48, 'gpt-6.1-sol': 0.63, 'kimi-k2.6': 0.59},
                                'cross': 0.2,
                                'null': 0.73,
                                'flags': ['borderline']},
 'context.life_stage': {'outcome': 'cut',
                        'repeat': {'claude-sonnet-5-5': 0.79, 'claude-haiku-5-5': 0.47, 'gpt-6.1-sol': 0.91, 'kimi-k2.6': 0.56},
                        'cross': 0.44,
                        'null': 0.39,
                        'flags': ['borderline']},
 'context.scope.text': {'outcome': 'pass',
                        'repeat': {'claude-sonnet-5-5': 0.86, 'claude-haiku-5-5': 0.69, 'gpt-6.1-sol': 0.82, 'kimi-k2.6': 0.73},
                        'cross': 0.47,
                        'null': 0.06,
                        'flags': ['borderline']},
 'context.scope.direction': {'outcome': 'cut',
                             'repeat': {'claude-sonnet-5-5': 0.84, 'claude-haiku-5-5': 0.6, 'gpt-6.1-sol': 0.78, 'kimi-k2.6': 0.68},
                             'cross': 0.37,
                             'null': 0.18,
                             'flags': ['borderline']},
 'salience.memory_type': {'outcome': 'interpretive',
                          'repeat': {'claude-sonnet-5-5': 0.85, 'claude-haiku-5-5': 0.73, 'gpt-6.1-sol': 0.8, 'kimi-k2.6': 0.72},
                          'cross': 0.36,
                          'null': 0.26,
                          'flags': ['borderline']},
 'salience.tether.type': {'outcome': 'pass',
                          'repeat': {'claude-sonnet-5-5': 0.81, 'claude-haiku-5-5': 0.71, 'gpt-6.1-sol': 0.81, 'kimi-k2.6': 0.71},
                          'cross': 0.53,
                          'null': 0.14,
                          'flags': ['borderline']},
 'salience.tether.referent': {'outcome': 'cut',
                              'repeat': {'claude-sonnet-5-5': 0.81, 'claude-haiku-5-5': 0.71, 'gpt-6.1-sol': 0.79, 'kimi-k2.6': 0.66},
                              'cross': 0.52,
                              'null': 0.14,
                              'flags': ['borderline'],
                              'cross_populated': 0.51},
 'salience.tether.stake': {'outcome': 'cut',
                           'repeat': {'claude-sonnet-5-5': 0.67, 'claude-haiku-5-5': 0.5, 'gpt-6.1-sol': 0.7, 'kimi-k2.6': 0.47},
                           'cross': 0.33,
                           'null': 0.27,
                           'flags': [],
                           'cross_populated': 0.18},
 'salience.retrieval_cues': {'outcome': 'cut',
                             'repeat': {'claude-sonnet-5-5': 0.58, 'claude-haiku-5-5': 0.36, 'gpt-6.1-sol': 0.86, 'kimi-k2.6': 0.42},
                             'cross': 0.18,
                             'null': 0.29,
                             'flags': [],
                             'cross_populated': 0.12},
 'salience.themes': {'outcome': 'cut',
                     'repeat': {'claude-sonnet-5-5': 0.53, 'claude-haiku-5-5': 0.32, 'gpt-6.1-sol': 0.59, 'kimi-k2.6': 0.41},
                     'cross': 0.06,
                     'null': 0.05,
                     'flags': [],
                     'cross_populated': 0.05},
 'salience.recurrence': {'outcome': 'cut',
                         'repeat': {'claude-sonnet-5-5': 0.72, 'claude-haiku-5-5': 0.51, 'gpt-6.1-sol': 0.55, 'kimi-k2.6': 0.67},
                         'cross': 0.2,
                         'null': 0.63,
                         'flags': ['borderline']},
 'salience.persistence.text': {'outcome': 'cut',
                               'repeat': {'claude-sonnet-5-5': 0.71, 'claude-haiku-5-5': 0.53, 'gpt-6.1-sol': 0.55, 'kimi-k2.6': 0.57},
                               'cross': 0.26,
                               'null': 0.68,
                               'flags': ['borderline']},
 'salience.persistence.decay': {'outcome': 'cut',
                                'repeat': {'claude-sonnet-5-5': 0.75, 'claude-haiku-5-5': 0.52, 'gpt-6.1-sol': 0.86, 'kimi-k2.6': 0.59},
                                'cross': 0.25,
                                'null': 0.72,
                                'flags': ['borderline']},
 'salience.linkage_strength': {'outcome': 'interpretive',
                               'repeat': {'claude-sonnet-5-5': 0.96, 'claude-haiku-5-5': 0.88, 'gpt-6.1-sol': 0.09, 'kimi-k2.6': 0.94},
                               'cross': 0.5,
                               'null': 0.43,
                               'flags': ['borderline']},
 'salience.function': {'outcome': 'pass',
                       'repeat': {'claude-sonnet-5-5': 0.92, 'claude-haiku-5-5': 0.68, 'gpt-6.1-sol': 0.87, 'kimi-k2.6': 0.76},
                       'cross': 0.52,
                       'null': 0.73,
                       'flags': ['borderline']},
 'salience.resilience': {'outcome': 'cut',
                         'repeat': {'claude-sonnet-5-5': 0.7, 'claude-haiku-5-5': 0.62, 'gpt-6.1-sol': 0.71, 'kimi-k2.6': 0.57},
                         'cross': 0.38,
                         'null': 0.39,
                         'flags': [],
                         'cross_populated': 0.11},
 'salience.trajectory': {'outcome': 'cut',
                         'repeat': {'claude-sonnet-5-5': 0.81, 'claude-haiku-5-5': 0.67, 'gpt-6.1-sol': 0.84, 'kimi-k2.6': 0.65},
                         'cross': 0.42,
                         'null': 0.54,
                         'flags': ['borderline']},
 'motivation.action_tendency': {'outcome': 'pass',
                                'repeat': {'claude-sonnet-5-5': 0.82, 'claude-haiku-5-5': 0.66, 'gpt-6.1-sol': 0.73, 'kimi-k2.6': 0.72},
                                'cross': 0.4,
                                'null': 0.2,
                                'flags': ['borderline']},
 'motivation.need': {'outcome': 'pass',
                     'repeat': {'claude-sonnet-5-5': 0.85, 'claude-haiku-5-5': 0.68, 'gpt-6.1-sol': 0.8, 'kimi-k2.6': 0.73},
                     'cross': 0.5,
                     'null': 0.43,
                     'flags': ['borderline']},
 'motivation.temporal_focus': {'outcome': 'pass',
                               'repeat': {'claude-sonnet-5-5': 0.86, 'claude-haiku-5-5': 0.61, 'gpt-6.1-sol': 0.84, 'kimi-k2.6': 0.82},
                               'cross': 0.56,
                               'null': 0.12,
                               'flags': []},
 'motivation.risk_posture': {'outcome': 'interpretive',
                             'repeat': {'claude-sonnet-5-5': 0.8, 'claude-haiku-5-5': 0.46, 'gpt-6.1-sol': 0.83, 'kimi-k2.6': 0.73},
                             'cross': 0.18,
                             'null': 0.62,
                             'flags': ['borderline']},
 'motivation.coping': {'outcome': 'pass',
                       'repeat': {'claude-sonnet-5-5': 0.82, 'claude-haiku-5-5': 0.69, 'gpt-6.1-sol': 0.73, 'kimi-k2.6': 0.74},
                       'cross': 0.54,
                       'null': 0.45,
                       'flags': ['borderline']}}

RUN3_SOURCE = 'experiments/2026-10-18-run3/RESULTS.md sections 1-2 (pooled, 150 texts, 5-of-8 rule after lever 3, thresholds frozen in experiment-plan-run3.md section 7 at 974408e; R18 reading (b) decides, reading (a) frozen beside)'
RUN3_RULE_MIN = 5  # a field holds across the market when >= 5 of the 8 models hold it (three voters by their classing run + >= 2 of the 5 new arms)
RUN3 = {
 'narrative.harm': {'holds_a': 5, 'holds_b': 6, 'of': 8, 'majority_texts': 133, 'majority_null_share': 0.36, 'texts_without_judge': 0, 'framing_bound': 0.75, 'ruling': 'R19',
    'arms': {
             'gemini-4-argon': {'repeat': 0.88, 'agree': 0.77, 'coverage_a': 0.59, 'coverage_b': 0.89, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.81, 'agree': 0.74, 'coverage_a': 0.56, 'coverage_b': 0.89, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.97, 'agree': 0.55, 'coverage_a': 0.3, 'coverage_b': 0.89, 'a': 'uncovered', 'b': 'repeats only', 'borderline': False},
             'mistral-large-4': {'repeat': 0.64, 'agree': 0.73, 'coverage_a': 0.61, 'coverage_b': 0.88, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.98, 'agree': 0.64, 'coverage_a': 0.41, 'coverage_b': 0.89, 'a': 'uncovered', 'b': 'holds', 'borderline': True}
    }},
 'narrative.summary': {'holds_a': 8, 'holds_b': 8, 'of': 8, 'majority_texts': 150, 'majority_null_share': 0.0, 'texts_without_judge': 0, 'framing_bound': 0.99, 'ruling': 'R20 (closed on the completed judge, 2026-10-18)',
    'arms': {
             'gemini-4-argon': {'repeat': 1.0, 'agree': 0.99, 'coverage_a': 1.0, 'coverage_b': 1.0, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.96, 'agree': 0.98, 'coverage_a': 0.99, 'coverage_b': 1.0, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.92, 'agree': 0.86, 'coverage_a': 0.99, 'coverage_b': 1.0, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.89, 'agree': 0.95, 'coverage_a': 0.97, 'coverage_b': 0.99, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.96, 'agree': 0.73, 'coverage_a': 0.85, 'coverage_b': 1.0, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'narrative.meaning': {'holds_a': 6, 'holds_b': 6, 'of': 8, 'majority_texts': 140, 'majority_null_share': 0.44, 'texts_without_judge': 0, 'framing_bound': 0.73, 'ruling': 'R21',
    'arms': {
             'gemini-4-argon': {'repeat': 0.92, 'agree': 0.6, 'coverage_a': 0.84, 'coverage_b': 0.93, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'qwen3.8-2.4t': {'repeat': 0.83, 'agree': 0.82, 'coverage_a': 0.61, 'coverage_b': 0.93, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.8, 'agree': 0.53, 'coverage_a': 0.83, 'coverage_b': 0.93, 'a': 'does not hold', 'b': 'does not hold', 'borderline': True},
             'mistral-large-4': {'repeat': 0.69, 'agree': 0.71, 'coverage_a': 0.71, 'coverage_b': 0.93, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.95, 'agree': 0.71, 'coverage_a': 0.6, 'coverage_b': 0.93, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'narrative.turning_point': {'holds_a': 3, 'holds_b': 7, 'of': 8, 'majority_texts': 149, 'majority_null_share': 0.87, 'texts_without_judge': 0, 'framing_bound': 0.65, 'ruling': 'R22',
    'arms': {
             'gemini-4-argon': {'repeat': 0.85, 'agree': 0.61, 'coverage_a': 0.12, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.76, 'agree': 0.73, 'coverage_a': 0.17, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.85, 'agree': 0.5, 'coverage_a': 0.23, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.63, 'agree': 0.69, 'coverage_a': 0.13, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.94, 'agree': 0.45, 'coverage_a': 0.16, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'holds', 'borderline': False}
    }},
 'narrative.self_position': {'holds_a': 3, 'holds_b': 8, 'of': 8, 'majority_texts': 150, 'majority_null_share': 0.82, 'texts_without_judge': 0, 'framing_bound': 0.97, 'ruling': 'R23',
    'arms': {
             'gemini-4-argon': {'repeat': 0.97, 'agree': 0.96, 'coverage_a': 0.21, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.9, 'agree': 0.89, 'coverage_a': 0.28, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.97, 'agree': 0.91, 'coverage_a': 0.19, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.89, 'agree': 0.95, 'coverage_a': 0.21, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.99, 'agree': 0.91, 'coverage_a': 0.15, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False}
    }},
 'emotion.primary': {'holds_a': 7, 'holds_b': 7, 'of': 8, 'majority_texts': 124, 'majority_null_share': 0.13, 'texts_without_judge': 0, 'framing_bound': 0.84, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.87, 'agree': 0.7, 'coverage_a': 0.75, 'coverage_b': 0.83, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.83, 'agree': 0.78, 'coverage_a': 0.74, 'coverage_b': 0.83, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.85, 'agree': 0.59, 'coverage_a': 0.77, 'coverage_b': 0.83, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.61, 'agree': 0.72, 'coverage_a': 0.71, 'coverage_b': 0.82, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.93, 'agree': 0.5, 'coverage_a': 0.61, 'coverage_b': 0.83, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'emotion.valence.text': {'holds_a': 8, 'holds_b': 8, 'of': 8, 'majority_texts': 148, 'majority_null_share': 0.11, 'texts_without_judge': 0, 'framing_bound': 0.9, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.94, 'agree': 0.8, 'coverage_a': 0.93, 'coverage_b': 0.99, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.88, 'agree': 0.81, 'coverage_a': 0.91, 'coverage_b': 0.99, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.92, 'agree': 0.55, 'coverage_a': 0.95, 'coverage_b': 0.99, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.72, 'agree': 0.83, 'coverage_a': 0.85, 'coverage_b': 0.98, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'gpt-oss-120b': {'repeat': 0.97, 'agree': 0.46, 'coverage_a': 0.73, 'coverage_b': 0.99, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'emotion.intensity.value': {'holds_a': 7, 'holds_b': 7, 'of': 8, 'majority_texts': 137, 'majority_null_share': None, 'texts_without_judge': 0, 'framing_bound': 0.97, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.97, 'agree': 0.75, 'coverage_a': 0.91, 'coverage_b': 0.91, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.94, 'agree': 0.91, 'coverage_a': 0.91, 'coverage_b': 0.91, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.87, 'agree': 0.58, 'coverage_a': 0.91, 'coverage_b': 0.91, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.89, 'agree': 0.52, 'coverage_a': 0.9, 'coverage_b': 0.9, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'gpt-oss-120b': {'repeat': 0.98, 'agree': 0.55, 'coverage_a': 0.49, 'coverage_b': 0.49, 'a': 'uncovered', 'b': 'uncovered', 'borderline': True}
    }},
 'emotion.bodily_sensation': {'holds_a': 3, 'holds_b': 8, 'of': 8, 'majority_texts': 150, 'majority_null_share': 0.78, 'texts_without_judge': 0, 'framing_bound': 0.98, 'ruling': 'R24',
    'arms': {
             'gemini-4-argon': {'repeat': 0.99, 'agree': 0.97, 'coverage_a': 0.25, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.97, 'agree': 0.97, 'coverage_a': 0.25, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.99, 'agree': 0.95, 'coverage_a': 0.21, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.91, 'agree': 0.95, 'coverage_a': 0.25, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.99, 'agree': 0.97, 'coverage_a': 0.2, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': False}
    }},
 'emotion.appraisal.attribution': {'holds_a': 3, 'holds_b': 5, 'of': 8, 'majority_texts': 150, 'majority_null_share': 0.84, 'texts_without_judge': 0, 'framing_bound': 0.86, 'ruling': 'R25',
    'arms': {
             'gemini-4-argon': {'repeat': 0.89, 'agree': 0.39, 'coverage_a': 0.49, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'repeats only', 'borderline': True},
             'qwen3.8-2.4t': {'repeat': 0.78, 'agree': 0.44, 'coverage_a': 0.43, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.93, 'agree': 0.23, 'coverage_a': 0.7, 'coverage_b': 1.0, 'a': 'repeats only', 'b': 'repeats only', 'borderline': False},
             'mistral-large-4': {'repeat': 0.61, 'agree': 0.39, 'coverage_a': 0.48, 'coverage_b': 0.99, 'a': 'uncovered', 'b': 'does not hold', 'borderline': True},
             'gpt-oss-120b': {'repeat': 0.89, 'agree': 0.44, 'coverage_a': 0.43, 'coverage_b': 1.0, 'a': 'uncovered', 'b': 'holds', 'borderline': True}
    }},
 'context.event_category': {'holds_a': 7, 'holds_b': 7, 'of': 8, 'majority_texts': 132, 'majority_null_share': 0.0, 'texts_without_judge': 0, 'framing_bound': 0.76, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.91, 'agree': 0.77, 'coverage_a': 0.88, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.78, 'agree': 0.82, 'coverage_a': 0.88, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.91, 'agree': 0.61, 'coverage_a': 0.87, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.65, 'agree': 0.75, 'coverage_a': 0.84, 'coverage_b': 0.87, 'a': 'does not hold', 'b': 'does not hold', 'borderline': True},
             'gpt-oss-120b': {'repeat': 0.9, 'agree': 0.59, 'coverage_a': 0.78, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'context.relationship': {'holds_a': 7, 'holds_b': 7, 'of': 8, 'majority_texts': 132, 'majority_null_share': 0.23, 'texts_without_judge': 0, 'framing_bound': 0.76, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.86, 'agree': 0.62, 'coverage_a': 0.75, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.72, 'agree': 0.73, 'coverage_a': 0.69, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.88, 'agree': 0.66, 'coverage_a': 0.73, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.57, 'agree': 0.6, 'coverage_a': 0.77, 'coverage_b': 0.87, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.88, 'agree': 0.49, 'coverage_a': 0.63, 'coverage_b': 0.88, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'context.scope.text': {'holds_a': 5, 'holds_b': 5, 'of': 8, 'majority_texts': 144, 'majority_null_share': 0.03, 'texts_without_judge': 0, 'framing_bound': 0.8, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.87, 'agree': 0.65, 'coverage_a': 0.96, 'coverage_b': 0.96, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.68, 'agree': 0.54, 'coverage_a': 0.91, 'coverage_b': 0.96, 'a': 'does not hold', 'b': 'does not hold', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.89, 'agree': 0.59, 'coverage_a': 0.92, 'coverage_b': 0.96, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.35, 'agree': 0.36, 'coverage_a': 0.92, 'coverage_b': 0.95, 'a': 'does not hold', 'b': 'does not hold', 'borderline': True},
             'gpt-oss-120b': {'repeat': 0.9, 'agree': 0.08, 'coverage_a': 0.79, 'coverage_b': 0.96, 'a': 'repeats only', 'b': 'repeats only', 'borderline': False}
    }},
 'salience.tether.type': {'holds_a': 4, 'holds_b': 4, 'of': 8, 'majority_texts': 142, 'majority_null_share': 0.11, 'texts_without_judge': 0, 'framing_bound': 0.66, 'ruling': 'R26',
    'arms': {
             'gemini-4-argon': {'repeat': 0.81, 'agree': 0.47, 'coverage_a': 0.95, 'coverage_b': 0.95, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.7, 'agree': 0.65, 'coverage_a': 0.88, 'coverage_b': 0.95, 'a': 'does not hold', 'b': 'does not hold', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.81, 'agree': 0.32, 'coverage_a': 0.91, 'coverage_b': 0.95, 'a': 'repeats only', 'b': 'repeats only', 'borderline': False},
             'mistral-large-4': {'repeat': 0.47, 'agree': 0.51, 'coverage_a': 0.85, 'coverage_b': 0.94, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.87, 'agree': 0.22, 'coverage_a': 0.65, 'coverage_b': 0.95, 'a': 'repeats only', 'b': 'repeats only', 'borderline': False}
    }},
 'salience.function': {'holds_a': 3, 'holds_b': 7, 'of': 8, 'majority_texts': 146, 'majority_null_share': 0.82, 'texts_without_judge': 0, 'framing_bound': 0.92, 'ruling': 'R27',
    'arms': {
             'gemini-4-argon': {'repeat': 0.79, 'agree': 0.55, 'coverage_a': 0.33, 'coverage_b': 0.97, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.74, 'agree': 0.69, 'coverage_a': 0.28, 'coverage_b': 0.97, 'a': 'uncovered', 'b': 'holds', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.9, 'agree': 0.47, 'coverage_a': 0.11, 'coverage_b': 0.97, 'a': 'uncovered', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.6, 'agree': 0.42, 'coverage_a': 0.42, 'coverage_b': 0.97, 'a': 'uncovered', 'b': 'does not hold', 'borderline': True},
             'gpt-oss-120b': {'repeat': 0.8, 'agree': 0.4, 'coverage_a': 0.41, 'coverage_b': 0.97, 'a': 'uncovered', 'b': 'holds', 'borderline': True}
    }},
 'motivation.action_tendency': {'holds_a': 5, 'holds_b': 5, 'of': 8, 'majority_texts': 125, 'majority_null_share': 0.14, 'texts_without_judge': 0, 'framing_bound': 0.73, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.84, 'agree': 0.57, 'coverage_a': 0.82, 'coverage_b': 0.83, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.65, 'agree': 0.58, 'coverage_a': 0.77, 'coverage_b': 0.83, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.84, 'agree': 0.42, 'coverage_a': 0.77, 'coverage_b': 0.83, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'mistral-large-4': {'repeat': 0.56, 'agree': 0.72, 'coverage_a': 0.71, 'coverage_b': 0.83, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.84, 'agree': 0.15, 'coverage_a': 0.55, 'coverage_b': 0.83, 'a': 'repeats only', 'b': 'repeats only', 'borderline': False}
    }},
 'motivation.need': {'holds_a': 7, 'holds_b': 7, 'of': 8, 'majority_texts': 135, 'majority_null_share': 0.35, 'texts_without_judge': 0, 'framing_bound': 0.77, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.86, 'agree': 0.54, 'coverage_a': 0.89, 'coverage_b': 0.9, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.76, 'agree': 0.6, 'coverage_a': 0.78, 'coverage_b': 0.9, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'llama-4-maverick': {'repeat': 0.88, 'agree': 0.44, 'coverage_a': 0.85, 'coverage_b': 0.9, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'mistral-large-4': {'repeat': 0.55, 'agree': 0.7, 'coverage_a': 0.71, 'coverage_b': 0.89, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.84, 'agree': 0.46, 'coverage_a': 0.53, 'coverage_b': 0.9, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'motivation.temporal_focus': {'holds_a': 7, 'holds_b': 7, 'of': 8, 'majority_texts': 145, 'majority_null_share': 0.03, 'texts_without_judge': 0, 'framing_bound': 0.81, 'ruling': 'held under both readings; not re-ruled (R18-R28 addendum)',
    'arms': {
             'gemini-4-argon': {'repeat': 0.9, 'agree': 0.73, 'coverage_a': 0.97, 'coverage_b': 0.97, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.75, 'agree': 0.64, 'coverage_a': 0.93, 'coverage_b': 0.97, 'a': 'holds', 'b': 'holds', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.91, 'agree': 0.66, 'coverage_a': 0.94, 'coverage_b': 0.97, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'mistral-large-4': {'repeat': 0.53, 'agree': 0.65, 'coverage_a': 0.9, 'coverage_b': 0.96, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.89, 'agree': 0.5, 'coverage_a': 0.71, 'coverage_b': 0.97, 'a': 'holds', 'b': 'holds', 'borderline': False}
    }},
 'motivation.coping': {'holds_a': 4, 'holds_b': 5, 'of': 8, 'majority_texts': 129, 'majority_null_share': 0.51, 'texts_without_judge': 0, 'framing_bound': 0.81, 'ruling': 'R28',
    'arms': {
             'gemini-4-argon': {'repeat': 0.81, 'agree': 0.51, 'coverage_a': 0.61, 'coverage_b': 0.86, 'a': 'holds', 'b': 'holds', 'borderline': False},
             'qwen3.8-2.4t': {'repeat': 0.67, 'agree': 0.63, 'coverage_a': 0.49, 'coverage_b': 0.86, 'a': 'uncovered', 'b': 'does not hold', 'borderline': True},
             'llama-4-maverick': {'repeat': 0.79, 'agree': 0.4, 'coverage_a': 0.66, 'coverage_b': 0.86, 'a': 'repeats only', 'b': 'repeats only', 'borderline': True},
             'mistral-large-4': {'repeat': 0.47, 'agree': 0.51, 'coverage_a': 0.56, 'coverage_b': 0.85, 'a': 'does not hold', 'b': 'does not hold', 'borderline': False},
             'gpt-oss-120b': {'repeat': 0.8, 'agree': 0.44, 'coverage_a': 0.49, 'coverage_b': 0.86, 'a': 'uncovered', 'b': 'holds', 'borderline': True}
    }},
}

# ---------------------------------------------------------------------------
# 3e. Comparability class per unit and per field, and the profile manifests derived from it (R17, 2026-10-18).
#     Unit class: a core slot takes the class its run-2 ruling fixed (RUN2); any other scored unit takes it from run 1 pooled:
#     pass with populated-only cross >= 0.60, or pass with no populated-only figure (coded / numeric / boolean units, where
#     agreement is a kappa or an ICC over all answers) -> comparable; pass with populated-only cross < 0.60 -> null-driven;
#     interpretive -> interpretive; cut -> extractor-bound. Field class = class of the field's lead unit (LEAD_UNIT: the member
#     that carries the field's claim); the other members keep their own unit class as an annotation and ride with the field.
#     Run 3 (R18-R28, 2026-10-18 close): a comparable-tier lead unit that fails the market rule under R18 reading (b) re-classes
#     interpretive (the pre-registered recommendation; R26 tether), unless the judge has not reached every text for it (R20
#     summary: the class moves only on the completed judge); a hold at the minimum resting on cells within 0.05 of a threshold
#     carries the flags at_minimum / borderline (R25 attribution, R28 coping; action_tendency by the same rule).
#     Profiles: Essential = every affective field classed comparable; Extended = Essential + interpretive + null-driven;
#     Full = all 47; partner profiles select freely. Nothing is hand-listed: a change of class moves a field.
# ---------------------------------------------------------------------------
CLASSES = ['comparable', 'interpretive', 'null-driven', 'extractor-bound']
POPULATED_CROSS_MIN = 0.60
LEAD_UNIT = {'emotion.valence': 'emotion.valence.text', 'emotion.arousal': 'emotion.arousal.text', 'emotion.intensity': 'emotion.intensity.value',
             'emotion.appraisal.urgency': 'emotion.appraisal.urgency.text', 'emotion.appraisal.control': 'emotion.appraisal.control.text',
             'context.scope': 'context.scope.text', 'salience.tether': 'salience.tether.type', 'salience.persistence': 'salience.persistence.text'}
LEAD_WHY = {'emotion.intensity': 'value is the salience weight EDM carries (R5 kept it, R8)', 'salience.tether': 'type is the coded member; referent and stake are free-text companions',
            'context.scope': 'text is the v0.8.3 relational_perspective; direction is the merged directionality', 'salience.persistence': 'text is the v0.8.3 viscosity; decay is the merged temporal_decay'}
for _p in ('emotion.valence', 'emotion.arousal', 'emotion.appraisal.urgency', 'emotion.appraisal.control'): LEAD_WHY[_p] = 'text is the only scored member left after R5'

def unit_class(unit):
    """(class, basis) for one scored unit; class is None for a unit without an outcome (the R5-removed value members).
    The class before run 3 comes from _unit_class_runs_1_2; run 3 (RUN3) then re-classes a comparable-tier unit that fails the
    market rule under R18 reading (b) as interpretive, unless its judge coverage is incomplete (R20)."""
    cls, basis = _unit_class_runs_1_2(unit)
    r3 = RUN3.get(unit)
    if r3 is None or cls is None: return cls, basis
    verdict_b = r3['holds_b'] >= RUN3_RULE_MIN; verdict_a = r3['holds_a'] >= RUN3_RULE_MIN
    pending = (not verdict_b) and r3['texts_without_judge'] > 0
    flags = []
    if verdict_b and r3['holds_b'] == RUN3_RULE_MIN:
        flags.append('at_minimum')
        if any(a['b'] == 'holds' and a['borderline'] for a in r3['arms'].values()): flags.append('borderline')
    if pending: flags.append('judge_incomplete')
    run3 = {'holds_a': r3['holds_a'], 'holds_b': r3['holds_b'], 'of': r3['of'], 'verdict_a': 'holds' if verdict_a else 'fails', 'verdict_b': 'holds' if verdict_b else 'fails',
            'reading': 'R18: reading (b) decides prospectively (a null-valued answer counts as covered); reading (a), the frozen literal clause, is reported beside', 'arms': r3['arms'],
            'majority_texts': r3['majority_texts'], 'majority_null_share': r3['majority_null_share'], 'texts_without_judge': r3['texts_without_judge'], 'framing_bound': r3['framing_bound'],
            'flags': flags, 'ruling': r3['ruling'], 'source': RUN3_SOURCE}
    if verdict_b:
        why3 = f"run 3 holds across the market under reading (b) ({r3['holds_b']} of {r3['of']}; literal reading {r3['holds_a']} of {r3['of']})" + (f" [{', '.join(flags)}]" if flags else '')
    elif pending:
        why3 = f"run 3 fails under both readings ({r3['holds_b']} of {r3['of']}) but the judge reached only {150 - r3['texts_without_judge']} of 150 texts: class unchanged until the judge completes (R20)"
    else:
        cls = 'interpretive'; why3 = f"run 3 fails across the market under both readings ({r3['holds_b']} of {r3['of']}; pre-registered recommendation: interpretive; {r3['ruling']})"
    basis = {**basis, 'run3': run3, 'why': basis['why'] + '; ' + why3, 'ruling': basis['ruling'] + f"; run 3 {r3['ruling']}"}
    return cls, basis

def _unit_class_runs_1_2(unit):
    """(class, basis) from runs 1-2 only (R17 rule as written on 2026-10-18); run 3 is applied on top by unit_class."""
    if unit in RUN2:
        r = RUN2[unit]; a = r[r['arm_adopted']]
        return r['class'], {'run': 'run 2', 'ruling': r['ruling'], 'arm': r['arm_adopted'], 'outcome': a['outcome'], 'repeat': a['repeat'], 'cross': a['cross'],
                            'cross_populated_only': a['cross_populated_only'], 'null_rate': a['null_rate'], 'two_voter': a['two_voter'], 'why': r['class_basis'], 'source': RUN2_SOURCE}
    r = RUN1_POOLED[unit]
    cp = r.get('cross_populated')
    basis = {'run': 'run 1', 'ruling': 'R17 rule (R4 annotation)', 'outcome': r['outcome'], 'repeat': r['repeat'], 'cross': r['cross'], 'cross_populated_only': cp, 'null_rate': r['null'], 'flags': r['flags'], 'source': RUN1_SOURCE}
    if r['outcome'] == 'pass':
        if cp is None: cls, why = 'comparable', 'run-1 pass; agreement measured over all answers (no populated-only figure for this shape)'
        elif cp >= POPULATED_CROSS_MIN: cls, why = 'comparable', f'run-1 pass on populated answers (populated-only cross {cp:.2f} >= {POPULATED_CROSS_MIN:.2f})'
        else: cls, why = 'null-driven', f'run-1 pass carried by agreement on null (populated-only cross {cp:.2f} < {POPULATED_CROSS_MIN:.2f}; null {r["null"]:.2f})'
    elif r['outcome'] == 'interpretive': cls, why = 'interpretive', 'run-1 interpretive (repeatability met by >= 3 of 4, cross missed)'
    elif r['outcome'] == 'cut': cls, why = 'extractor-bound', 'run-1 cut (repeatability missed by >= 2 of 4; Sonnet 5.5 alone meets the bar on most such units)'
    else: cls, why = None, 'no outcome (value member never populated; removed by R5)'
    basis['why'] = why
    return cls, basis

def field_class(path):
    cls, basis = unit_class(LEAD_UNIT.get(path, path))
    return cls, {**basis, 'lead_unit': LEAD_UNIT.get(path, path), 'lead_unit_why': LEAD_WHY.get(path, 'the field is itself the scored unit')}

COMPARABILITY = {p: field_class(p)[0] for p in ALL_09}
_bad = [p for p in ALL_09 if COMPARABILITY[p] not in CLASSES]
assert not _bad, f'fields without a comparability class: {_bad}'
PROFILE_CLASSES = {'essential': ('comparable',), 'extended': ('comparable', 'interpretive', 'null-driven'), 'full': tuple(CLASSES)}
PROFILES_09 = {prof: [p for p in ALL_09 if COMPARABILITY[p] in cls] for prof, cls in PROFILE_CLASSES.items()}
PROFILE_RULE = ('R17 (2026-10-18): profile membership is derived from the comparability class, not chosen. Essential = every affective field classed '
                '"comparable" (run-1 pass on populated answers, or run-2 pass, and - for the 19 comparable-tier fields tested across vendors in run 3 - holding the market rule under R18 reading (b), R19-R28); Extended = Essential + "interpretive" + "null-driven"; Full = all 47; '
                'partner profiles select freely from their base. Field class = class of the lead unit (LEAD_UNIT); sub-members ride with their field. '
                'Computed in scripts/v09_layout.py (COMPARABILITY, PROFILES_09); nothing hand-listed.')
PARTNER_BASE = {'partner:com.deepadata.journaling.v1': 'extended', 'partner:com.deepadata.therapy.v1': 'full',
                'partner:com.deepadata.companion.v1': 'extended', 'partner:com.deepadata.wiki.v1': 'extended'}
TRAIT_OPT_IN = {'partner:com.deepadata.therapy.v1'}  # discovery assumption for the draft manifests
def profile_fields(profile):
    return PROFILES_09[PARTNER_BASE.get(profile, profile)]

def unit_annotations(unit):
    """x_ annotations for one scored unit (a field path, or <field>.text / .value / .direction / .type / .referent / .stake / .decay)."""
    r = RUN1_POOLED.get(unit); out = {}
    if r:
        out['x_run1'] = {'outcome': r['outcome'], 'repeat': r['repeat'], 'cross': r['cross'], 'cross_populated_only': r.get('cross_populated'),
                         'null_rate': r['null'], 'flags': r['flags'], 'source': RUN1_SOURCE}
    if unit in RUN2:
        r2 = RUN2[unit]
        out['x_run2'] = {'ruling': r2['ruling'], 'arm_adopted': r2['arm_adopted'], 'A_v083_text': r2['A'], 'B_v09_rules': r2['B'], 'voters': VOTERS, 'source': RUN2_SOURCE}
    if r or unit in RUN2:
        cls, basis = unit_class(unit)
        if cls: out['x_comparability'] = cls; out['x_comparability_basis'] = basis
    if unit in VALUE_REMOVED: out['x_status'] = 'removed by R5 (2026-10-18): never populated in run 1; member deleted from the draft 2026-10-18'
    if unit in VALUE_KEPT: out['x_status'] = 'kept by R5 (2026-10-18): per-extractor numeric salience weight (R8)'
    if out: out['x_rulings'] = RULINGS
    return out

def field_annotations(path):
    """annotations for a v0.9 affective field: its own unit statistics when the field is itself a scored unit, plus the field-level
    class from its lead unit and the profiles that class derives (R17). trait.* and infrastructure paths get none."""
    if path not in COMPARABILITY: return {}
    out = unit_annotations(path) if (path in RUN1_POOLED or path in RUN2) else {}
    cls, basis = field_class(path)
    out['x_comparability'] = cls
    out['x_comparability_basis'] = basis
    out['x_profiles'] = [prof for prof in PROFILES_09 if path in PROFILES_09[prof]]
    out['x_profile_rule'] = PROFILE_RULE
    out['x_rulings'] = RULINGS
    return out

def run1_for_field(path):
    """annotations for every scored unit under a v0.9 field path (for the crosswalk record)."""
    return {u: unit_annotations(u) for u in RUN1_POOLED if u == path or u.startswith(path + '.')}

def membership_table():
    """R17 membership as markdown: one row per affective field with its class, lead unit and the figure behind it."""
    def fig(b):
        rep = ' / '.join(f'{v:.2f}' if v is not None else 'n/a' for v in b['repeat'].values())
        who = 'S / H / G / K' if len(b['repeat']) == 4 else 'S / G / K'
        cp = f", populated-only {b['cross_populated_only']:.2f}" if b.get('cross_populated_only') is not None else ''
        cross = f"{b['cross']:.2f}" if b['cross'] is not None else 'n/a'
        head = (f"run 2 Arm {b['arm']} {b['outcome']} ({b['ruling']})" if b['run'] == 'run 2' else f"run 1 {b['outcome']}")
        r3 = b.get('run3')
        tail = (f"; run 3 (b) {r3['holds_b']} of {r3['of']} {r3['verdict_b']} (a: {r3['holds_a']})" + (f" [{', '.join(r3['flags'])}]" if r3['flags'] else '')) if r3 else ''
        return f"{head}: rep {who} {rep}; cross {cross}{cp}; null {b['null_rate']:.2f}{tail}"
    lines = ['| Field | Class | Profiles | Lead unit | Figure |', '|---|---|---|---|---|']
    for p in ALL_09:
        cls, b = field_class(p)
        profs = ', '.join(prof for prof in PROFILES_09 if p in PROFILES_09[prof])
        lead = b['lead_unit'] if b['lead_unit'] != p else '(field)'
        lines.append(f"| `{p}` | {cls} | {profs} | `{lead}` | {fig(b)} |")
    counts = Counter(COMPARABILITY.values())
    lines += ['', f"Counts: {', '.join(f'{c} {counts[c]}' for c in CLASSES)}; Essential {len(PROFILES_09['essential'])}, Extended {len(PROFILES_09['extended'])}, Full {len(PROFILES_09['full'])}."]
    return '\n'.join(lines)

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
        'valence': {'text': val, 'codings': ([edm('valence', val)] + VALENCE_CODES.get(val, [])) if val else []},  # R5: no value member
        'arousal': {'text': None, 'codings': []},  # R5: born as coded text
        'intensity': dimension(None, w, [eml('intensity-dimension', 'intensity')] if w is not None else []),
        'meta': g('constellation', 'meta_emotional_state'),
        'bodily_sensation': g('constellation', 'somatic_signature'),
        'temporal_profile': coded('temporal_profile', g('constellation', 'temporal_rhythm'), PROFILE_CODES),
        'appraisal': {
            'urgency': {'text': urg, 'codings': ([edm('urgency', urg), eml('ema-appraisals', 'urgency')] + URGENCY_CODES.get(urg, [])) if urg else []},  # R5
            'control': {'text': ctl, 'codings': ([edm('control', ctl), eml('scherer-appraisals', 'control')] + CONTROL_CODES.get(ctl, [])) if ctl else []},  # R5
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
    cues, cues_overflow = cues[:RETRIEVAL_CUES_MAX], cues[RETRIEVAL_CUES_MAX:]  # R16: echo first, cap 3; the rest preserved verbatim below
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
    leg = {}
    if legacy: leg['v0_8_3_cut_fields'] = legacy
    if cues_overflow: leg['retrieval_cues_overflow'] = cues_overflow
    if leg: ext[LEGACY_EXT] = leg
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
            elif k == 'appraisal':
                sub = out[dom][k]
                for sk in list(sub.keys()):
                    if f'{path}.{sk}' in allowed: continue
                    v = sub.pop(sk)
                    if not is_empty(v): moved[f'{path}.{sk}'] = v
                if not sub: out[dom].pop(k)
                continue
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
     'description': 'Draft record of the v0.9 relayout proposed in docs/discovery/ontology-crosswalk-2026-10/v0.9-proposal.md. Five affective domains are renamed (core->narrative, constellation->emotion, milky_way->context, gravity->salience, impulse->motivation); 57 affective fields become %d (%d carried by rename/move, %d merged into others, %d cut with text preserved in extensions, %d moved to an opt-in trait profile, %d new); every categorical field becomes text + codings; emotion.intensity is a dimension with the v0.8.3 numeric weight beside an ordinal text (the value member of valence / arousal / urgency / control was removed by R5, 2026-10-18, never populated in run 1). Profile membership is derived from the comparability class of each field (R17). No artifact text changes: scripts/v09_layout.py in the discovery folder proves the scalar multiset of the affective domains is identical before and after.' % (AFFECTIVE_COUNT, len(renamed), len(merged), len(cut), len(trait), n_new),
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
        'comparability_classes': dict(sorted(Counter(COMPARABILITY.values()).items())),
        'profile_sizes': {k: len(v) for k, v in PROFILES_09.items()},
        'values_deprecated': len(DEPRECATED_VALUES),
        'values_renamed': 0,
        'text_changes_required': 0,
     },
     'domain_renames': {'core': 'narrative', 'constellation': 'emotion', 'milky_way': 'context', 'gravity': 'salience', 'impulse': 'motivation'},
     'disposition_rule': 'One disposition per v0.8.3 field (carried / renamed / reshaped / merged / cut-to-extensions / moved-to-trait; new v0.9 fields are added) and one per canonical value (carried / carried (deprecated) / cut-to-extensions / moved-to-trait; new vocabulary values are added). carried = field name unchanged (domain rename or move only); renamed = field name changes; reshaped = enum or number becomes a dimension; merged = the v0.9 target has more than one v0.8.3 source. The uniform {text, codings} wrapping is recorded as shape_from / shape_to on each row. Value words never change. Audited by scripts/crosswalk_audit.py (crosswalk-audit-2026-10-18.md).',
     'field_map': field_rows(),
     'new_fields': [{'path': p, 'shape': s if p + '.value' not in VALUE_REMOVED else 'coded (value removed, R5)', 'disposition': 'added', 'note': n, 'populated_by_migration': False, 'v09': {'description': DESC[p][0], 'constraints': DESC[p][1], 'profiles': profiles_of_09(p), 'comparability': COMPARABILITY.get(p), 'run1_annotations': run1_for_field(p)} if p in DESC else None} for p, s, n in NEW_FIELDS],
     'new_values': new_value_rows(),
     'trait_profile': {
        'fields': TRAIT_FIELDS,
        'rule': 'Not part of any canonical profile. A partner profile opts in by listing trait.* in included_fields. Each value is recorded only as stated for this experience and is never aggregated into a person-level classification by the artifact.',
        'migration': 'A v0.8.3 artifact carrying attachment_style or regulation_state keeps them in trait.* only when the target profile opts in; otherwise they are preserved verbatim in extensions.' + LEGACY_EXT + '.out_of_profile_fields.',
     },
     'profiles': {'essential': PROFILES_09['essential'], 'extended': PROFILES_09['extended'], 'full': PROFILES_09['full'], 'trait_opt_in_partner_profiles': sorted(TRAIT_OPT_IN),
                  'comparability': COMPARABILITY, 'lead_units': LEAD_UNIT,
                  'rule': PROFILE_RULE + ' extensions is allowed in all three composites. text of coded fields is a recommended vocabulary (string; canonical list documented, not an enum); codings on the EDM vocabulary are enumerated. Draft schema: docs/discovery/ontology-crosswalk-2026-10/draft-schema/.'},
     'coding_shape': {
        'coded': {'text': 'string (the interpretation; mandatory when the field is populated)', 'codings': [{'system': 'URI', 'version': 'string', 'code': 'string', 'display': 'string', 'relation': 'exact | broader | narrower | related (default exact)'}]},
        'dimension': {'text': 'ordinal label or null', 'value': 'number or null (never derived from text by migration)', 'codings': '[...]', 'note': 'emotion.intensity only (R5)'},
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
        'steps': ['1. Rename domains and fields per field_map.', '2. Wrap categorical values as {text, codings} and apply codes from the vocabulary files; text is copied, never translated.', '3. Carry numeric intensity into emotion.intensity.value; valence / urgency / control carry text + codings only (R5: no value member).', '4. Concatenate echo + recall_triggers + retrieval_keys, in that order, into salience.retrieval_cues, keeping at most three (R16); preserve any further value verbatim in extensions.' + LEGACY_EXT + '.retrieval_cues_overflow; append higher_order_emotion to emotion.secondary; collect narrative_arc and arc_type into narrative.arc[].', '5. Move attachment_style and regulation_state to trait.* only if the target profile opts in; otherwise preserve them in extensions.', '6. Copy cut-field values into extensions.' + LEGACY_EXT + '.v0_8_3_cut_fields.', '7. Prune to the target profile manifest (derived from comparability class, R17); any populated field outside it goes to extensions.' + LEGACY_EXT + '.out_of_profile_fields.', '8. Set meta.version.'],
        'reference_implementation': 'docs/discovery/ontology-crosswalk-2026-10/scripts/v09_layout.py',
     },
    }

if __name__ == '__main__':
    if sys.argv[1:2] == ['--membership']:
        print(membership_table()); sys.exit(0)
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
    print('comparability (R17):', dict(Counter(COMPARABILITY.values())))
    print('profiles (derived):', {k: len(v) for k, v in PROFILES_09.items()})
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
