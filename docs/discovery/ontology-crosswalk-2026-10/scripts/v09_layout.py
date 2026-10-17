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
import json, sys, os
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
        'affective_field_count_before': 57,
        'affective_field_count_after': AFFECTIVE_COUNT,
        'values_deprecated': len(DEPRECATED_VALUES),
        'values_renamed': 0,
        'text_changes_required': 0,
     },
     'domain_renames': {'core': 'narrative', 'constellation': 'emotion', 'milky_way': 'context', 'gravity': 'salience', 'impulse': 'motivation'},
     'field_map': [{'from': o, 'to': n, 'action': act, 'shape': shape, 'note': note} for o, n, act, shape, note in FIELD_MAP],
     'new_fields': [{'path': p, 'shape': s, 'note': n, 'populated_by_migration': False} for p, s, n in NEW_FIELDS],
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
