"""Write the synthetic replacements for the seven examples/*.json artifacts (v0.8.3 layout).

Usage:
  python -I scripts/make_synthetic.py synthetic-examples

The published examples share one source text that describes a real person's situation. These files replace it with
an invented one of similar emotional complexity (a milestone, a chronic constraint, a supportive community, a stated
insight) and invent fresh texts for the three partner examples that carried their own. Nothing here refers to a real
person: no names, handles, diagnoses, places or dates that could identify anyone. Every value is hand-written for
discovery and is NOT an extraction output; telemetry says so. Field structure, profile membership, enum choices and
value counts follow the published examples so the synthetic set exercises the same schema paths.

The files validate against schema/edm.v0.8.{essential,extended,full}.schema.json (see scripts/validate_synthetic.mjs).
examples/ is not touched.
"""
import json, os, sys, uuid, random

out_dir = sys.argv[1]
os.makedirs(out_dir, exist_ok=True)

def uid(n):  # deterministic, v4-shaped, so the files are reproducible
    return str(uuid.UUID(int=random.Random(2026_10_17 * 100 + n).getrandbits(128), version=4))
OWNER = {'a': 'vp-SYN00000000000000A1', 'b': 'vp-SYN00000000000000B2', 'c': 'vp-SYN00000000000000C3', 'd': 'vp-SYN00000000000000D4'}
MODEL = 'synthetic-hand-written'  # extraction_model must be a string; this one says what the file is
NOTE = 'SYNTHETIC example written for discovery (docs/discovery/ontology-crosswalk-2026-10); not an extraction output; no real person is described.'

# ---------------------------------------------------------------------------
# Canonical synthetic source text (replaces the competition-photos text shared by essential / extended / full / wiki)
# milestone: first solo verse, recording arrived | chronic constraint: unnamed long-term condition limiting breath and stamina
# supportive community: a mixed-age choir | stated insight: "everyone needs an hour a week that is only theirs"
# ---------------------------------------------------------------------------
CHOIR_TEXT = ("The recording of the choir's winter concert arrived this week, with my first solo verse in it. "
              "A long-term health condition has limited my breath and stamina for years, and the weekly rehearsals with people of every age keep both my lungs and my mood working. "
              "Standing at the front of the hall and hearing the room go quiet brought back the person who used to perform without thinking about it. "
              "What started as a neighbour's nudge three years ago has become the one hour a week that is only mine, and I have come to believe everyone needs an hour like that.")
CHOIR_TEXT_SHORT = ("The recording of the choir's winter concert arrived this week, with my first solo verse in it. "
                    "A long-term health condition has limited my breath and stamina for years, and the weekly rehearsals with people of every age keep both lungs and mood working. "
                    "Standing at the front of the hall and hearing the room go quiet brought back the person who used to perform without a second thought. "
                    "What started as a neighbour's nudge has become the one hour a week that is only mine.")

def governance(basis='user_defined', ttl=None, on_expiry='soft_delete', explainable=False, jurisdiction=None, **extra):
    g = {'jurisdiction': jurisdiction, 'retention_policy': {'basis': basis, 'ttl_days': ttl, 'on_expiry': on_expiry},
         'subject_rights': {'portable': True, 'erasable': True, 'explainable': explainable}}
    g.update(extra); return g

def meta(n, profile, owner, created, **extra):
    m = {'id': uid(n), 'version': '0.8.3', 'profile': profile, 'created_at': created, 'owner_user_id': OWNER[owner],
         'consent_basis': 'consent', 'visibility': 'private', 'pii_tier': 'moderate'}
    m.update(extra); return m

files = {}

files['example-essential-profile.json'] = {
 'meta': meta(1, 'essential', 'a', '2026-10-17T09:12:03.000Z'),
 'core': {'anchor': 'choir winter concert', 'spark': 'concert recording arrived', 'wound': 'stamina lost to illness',
          'fuel': 'choir of every age', 'bridge': 'performing through limits', 'echo': 'the hall going quiet'},
 'constellation': {'emotion_primary': 'joy', 'emotion_subtone': ['proud', 'grateful', 'nostalgic', 'supported'], 'narrative_arc': 'overcoming'},
 'governance': governance(jurisdiction='GDPR'),
 'telemetry': {'entry_confidence': 0.94, 'extraction_model': MODEL, 'extraction_provider': None},
}

files['example-extended-profile.json'] = {
 'meta': {**meta(2, 'extended', 'a', '2026-10-17T09:12:21.000Z'), 'updated_at': None, 'locale': 'en', 'source_type': 'text',
          'source_context': 'journal entry written after the concert recording arrived', 'consent_scope': 'personal memory archive',
          'tags': ['choir', 'resilience', 'community']},
 'core': {'anchor': 'choir winter concert', 'spark': 'concert recording arrived', 'wound': 'breath limited by illness',
          'fuel': 'choir of every age', 'bridge': 'still performing despite limits', 'echo': 'the hall going quiet', 'narrative': CHOIR_TEXT},
 'constellation': {'emotion_primary': 'joy', 'emotion_subtone': ['pride', 'gratitude', 'relief'], 'higher_order_emotion': 'quiet triumph',
                   'meta_emotional_state': 'grateful acceptance', 'interpersonal_affect': 'belonging', 'narrative_arc': 'overcoming',
                   'relational_dynamics': 'community_ritual', 'temporal_context': 'midlife', 'memory_type': 'milestone', 'media_format': 'audio',
                   'narrative_archetype': 'hero', 'symbolic_anchor': 'the solo verse', 'relational_perspective': 'community', 'temporal_rhythm': 'rising',
                   'identity_thread': 'performer despite limits', 'expressed_insight': 'everyone needs an hour a week that is only theirs',
                   'transformational_pivot': True, 'somatic_signature': 'breath held, then easy', 'arc_type': 'authenticity'},
 'milky_way': {'event_type': 'annual concert performance', 'location_context': 'community hall', 'associated_people': ['choir members', 'a neighbour'],
               'visibility_context': 'shared_publicly', 'tone_shift': 'effort to ease'},
 'gravity': {'emotional_weight': 0.82, 'valence': 'positive', 'tether_type': 'identity', 'recurrence_pattern': 'cyclical', 'strength_score': 0.9},
 'governance': governance(jurisdiction='GDPR', exportability='restricted', policy_labels=['personal', 'health-adjacent']),
 'telemetry': {'entry_confidence': 0.91, 'extraction_model': MODEL, 'extraction_provider': None, 'extraction_notes': NOTE},
}

files['example-full-profile.json'] = {
 'meta': {**meta(3, 'full', 'a', '2026-10-17T09:12:40.000Z'), 'updated_at': None, 'locale': 'en', 'parent_id': None, 'source_type': 'text',
          'source_context': 'journal entry written after the concert recording arrived', 'consent_scope': 'personal memory archive',
          'consent_revoked_at': None, 'tags': ['choir', 'resilience', 'community']},
 'core': {'anchor': 'choir winter concert', 'spark': 'concert recording arrived', 'wound': 'stamina lost to illness',
          'fuel': 'choir of every age', 'bridge': 'performer then, performer now', 'echo': 'the hall going quiet', 'narrative': CHOIR_TEXT},
 'constellation': {'emotion_primary': 'joy', 'emotion_subtone': ['proud', 'grateful', 'relieved', 'nostalgic'], 'higher_order_emotion': 'quiet triumph',
                   'meta_emotional_state': 'grateful acceptance', 'interpersonal_affect': 'belonging', 'narrative_arc': 'overcoming',
                   'relational_dynamics': 'community_ritual', 'temporal_context': 'midlife', 'memory_type': 'milestone', 'media_format': 'audio',
                   'narrative_archetype': 'hero', 'symbolic_anchor': 'the solo verse', 'relational_perspective': 'community', 'temporal_rhythm': 'rising',
                   'identity_thread': 'performer despite physical limits', 'expressed_insight': 'everyone needs an hour a week that is only theirs',
                   'transformational_pivot': True, 'somatic_signature': 'breath held, then easy', 'arc_type': 'authenticity'},
 'milky_way': {'event_type': 'annual concert', 'location_context': 'community hall', 'associated_people': ['choir members', 'a neighbour'],
               'visibility_context': 'shared_publicly', 'tone_shift': 'effort to ease'},
 'gravity': {'emotional_weight': 0.8, 'emotional_density': 'high', 'valence': 'positive', 'viscosity': 'high', 'gravity_type': 'identity restoration',
             'tether_type': 'identity', 'recall_triggers': ['the recording', 'stage lights', 'the quiet before the first note'],
             'retrieval_keys': ['choir', 'solo verse', 'stamina', 'community hall'], 'nearby_themes': ['chronic illness', 'self-care', 'community', 'performance'],
             'recurrence_pattern': 'cyclical', 'strength_score': 0.9, 'temporal_decay': 'slow', 'resilience_markers': ['acceptance', 'community', 'adaptation'],
             'adaptation_trajectory': 'improving'},
 'impulse': {'primary_energy': 'empowerment', 'drive_state': 'share', 'motivational_orientation': 'meaning', 'temporal_focus': 'present',
             'directionality': 'outward', 'social_visibility': 'collective', 'urgency': 'elevated', 'risk_posture': 'bold', 'agency_level': 'high',
             'regulation_state': 'regulated', 'attachment_style': 'secure', 'coping_style': 'seek_support'},
 'governance': governance(jurisdiction='GDPR', exportability='allowed', k_anonymity={'k': None, 'groups': []}, policy_labels=['personal', 'health-adjacent'], masking_rules=[]),
 'telemetry': {'entry_confidence': 0.93, 'extraction_model': MODEL, 'extraction_provider': None, 'extraction_notes': NOTE},
 'system': {'embeddings': [], 'indices': {'waypoint_ids': []}},
 'crosswalks': {'plutchik_primary': 'joy', 'geneva_emotion_wheel': 'Pride / Elation', 'DSM5_specifiers': None, 'ISO_27557_labels': None},
}

files['example-partner-wiki.json'] = {
 'meta': meta(4, 'partner:com.deepadata.wiki.v1', 'a', '2026-10-17T10:05:00.000Z'),
 'core': {'anchor': 'choir concerts', 'spark': 'concert recording arrived', 'wound': 'long-term illness', 'fuel': 'mixed-age choir community',
          'bridge': 'performing despite limits', 'echo': 'the hall going quiet', 'narrative': CHOIR_TEXT_SHORT},
 'constellation': {'emotion_primary': 'joy', 'emotion_subtone': ['pride', 'gratitude', 'relief'], 'narrative_arc': 'overcoming',
                   'identity_thread': 'performer despite limits', 'arc_type': 'transformation', 'temporal_context': 'midlife', 'memory_type': 'milestone'},
 'milky_way': {'event_type': 'choir concert', 'location_context': 'community hall', 'associated_people': ['choir members'],
               'visibility_context': 'shared_publicly', 'tone_shift': 'effort to ease'},
 'gravity': {'emotional_weight': 0.8, 'valence': 'positive', 'tether_type': 'identity', 'recurrence_pattern': 'cyclical', 'strength_score': 0.9},
 'governance': governance(),
 'telemetry': {'entry_confidence': 0.94, 'extraction_model': MODEL},
}

# ---------------------------------------------------------------------------
# Journaling: a dream about a late mentor's workshop (replaces the grandmother's-garden text)
# ---------------------------------------------------------------------------
files['example-partner-journaling.json'] = {
 'meta': meta(5, 'partner:com.deepadata.journaling.v1', 'b', '2026-10-17T06:40:00.000Z'),
 'core': {'anchor': 'morning pages', 'spark': "dream of the mentor's workshop", 'wound': "mentor's death", 'fuel': 'keeping the lesson going',
          'bridge': 'writing as practice', 'echo': 'the next piece handed over',
          'narrative': ("Woke from a dream set in the workshop my late mentor kept behind the house, where I learned to sand a chair leg without rushing. "
                        "In the dream he said nothing and just handed me the next piece. Two years since the funeral and I still save up things to tell him. "
                        "I started these morning pages because he said hands and words both need a daily practice. Maybe writing is how I keep the lesson going.")},
 'constellation': {'emotion_primary': 'longing', 'emotion_subtone': ['tenderness', 'gratitude', 'peace'], 'narrative_arc': 'reflection',
                   'identity_thread': 'apprentice who keeps the craft', 'arc_type': 'grief', 'temporal_context': 'midlife', 'memory_type': 'legacy_artifact'},
 'milky_way': {'event_type': 'morning journaling after a dream', 'location_context': "mentor's workshop (dreamed)", 'associated_people': ['my late mentor'],
               'visibility_context': 'private', 'tone_shift': 'grief to gratitude'},
 'gravity': {'emotional_weight': 0.78, 'valence': 'mixed', 'tether_type': 'person', 'recurrence_pattern': 'cyclical', 'strength_score': 0.75},
 'governance': governance(),
 'telemetry': {'entry_confidence': 0.92, 'extraction_model': MODEL},
}

# ---------------------------------------------------------------------------
# Companion: a department presentation on Friday (replaces the job-interview text)
# ---------------------------------------------------------------------------
files['example-partner-companion.json'] = {
 'meta': meta(6, 'partner:com.deepadata.companion.v1', 'c', '2026-10-17T20:30:00.000Z'),
 'core': {'anchor': 'department presentation on Friday', 'spark': 'fear of being judged', 'wound': 'not being taken seriously', 'fuel': 'rehearsing out loud',
          'bridge': 'dread to cautious confidence', 'echo': 'tougher rooms before',
          'narrative': ("The user talked about presenting to the whole department on Friday, the first time they will speak in front of senior staff. "
                        "They listed what could go wrong, then noticed that most of it was unlikely and that they had rehearsed more than anyone would expect. "
                        "Talking it through moved them from dread to cautious confidence. They said they had presented to tougher rooms during their training and had simply forgotten it.")},
 'constellation': {'emotion_primary': 'anxiety', 'emotion_subtone': ['hope', 'vulnerability', 'determination'], 'narrative_arc': 'overcoming',
                   'interpersonal_affect': 'openness', 'relational_dynamics': 'companionship', 'identity_thread': 'capable but self-doubting',
                   'arc_type': 'threshold', 'temporal_rhythm': 'rising'},
 'milky_way': {'event_type': 'pre-presentation support conversation', 'visibility_context': 'private', 'tone_shift': 'dread to confidence'},
 'gravity': {'emotional_weight': 0.7, 'valence': 'mixed', 'tether_type': 'event', 'recurrence_pattern': 'cyclical', 'strength_score': 0.66},
 'governance': governance(),
 'telemetry': {'entry_confidence': 0.88, 'extraction_model': MODEL},
}

# ---------------------------------------------------------------------------
# Therapy: the peacekeeper role reopened by a sibling's comment (replaces the father's-criticism text; no diagnosis)
# Note for the v0.9 experiment: this text contains a stated self-position ("the one who keeps the peace").
# ---------------------------------------------------------------------------
files['example-partner-therapy.json'] = {
 'meta': {**meta(7, 'partner:com.deepadata.therapy.v1', 'd', '2026-10-17T14:30:00.000Z'), 'pii_tier': 'high'},
 'core': {'anchor': 'peacekeeper role', 'spark': "sibling's comment at dinner", 'wound': 'never allowed to be upset', 'fuel': 'therapeutic insight',
          'bridge': 'dinner reaction to childhood role', 'echo': "managing everyone's mood",
          'narrative': ("Session focused on how a sibling's offhand comment at a family dinner reopened an old pattern. "
                        "Client described being the one expected to keep the peace since childhood and noticed they had apologised for a disagreement they did not start. "
                        "Named the moment when they said 'I have been managing everyone's mood since I was ten.' "
                        "First time explicitly connecting the dinner reaction to the childhood role.")},
 'constellation': {'emotion_primary': 'sadness', 'emotion_subtone': ['anxiety', 'anger', 'relief'], 'narrative_arc': 'overcoming',
                   'relational_dynamics': 'sibling_bond', 'identity_thread': 'the one who keeps the peace', 'arc_type': 'reconciliation',
                   'transformational_pivot': True, 'somatic_signature': 'jaw tight when describing the dinner'},
 'milky_way': {'event_type': 'therapy session', 'location_context': "therapist's office", 'associated_people': ['sibling', 'parents'],
               'visibility_context': 'private', 'tone_shift': 'resentment to insight'},
 'gravity': {'emotional_weight': 0.86, 'tether_type': 'person', 'recall_triggers': ['family dinners', 'raised voices', 'being asked to smooth things over'],
             'retrieval_keys': ['sibling', 'peacekeeper', 'apology', 'family role'], 'nearby_themes': ['self-worth', 'boundaries', 'family roles', 'validation'],
             'recurrence_pattern': 'chronic', 'strength_score': 0.84, 'temporal_decay': 'slow',
             'resilience_markers': ['naming the pattern', 'emotional awareness', 'willingness to examine'], 'adaptation_trajectory': 'improving'},
 'impulse': {'regulation_state': 'regulated', 'agency_level': 'medium', 'coping_style': 'process', 'attachment_style': 'anxious'},
 'governance': governance(basis='legal', ttl=2555, on_expiry='anonymize', explainable=True),
 'telemetry': {'entry_confidence': 0.95, 'extraction_model': MODEL},
 'system': {'embeddings': None, 'indices': None},
 'crosswalks': {'plutchik_primary': 'sadness', 'geneva_emotion_wheel': 'disappointment', 'DSM5_specifiers': None, 'ISO_27557_labels': None},
}

for name, doc in files.items():
    with open(os.path.join(out_dir, name), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False); fh.write('\n')
print(f'{len(files)} synthetic examples written to {out_dir}')
