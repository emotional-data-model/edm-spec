# Generic naming proposal — old → new mapping (v0.8.3 → proposed v0.9)

Discovery output, 2026-10-17. Not normative; a v0.9 change would go through `VERSIONING_POLICY.md` with a `schema/crosswalks/v0.8.3_to_v0.9.0.json`.

## Domain renames (as requested)

| v0.8.3 domain | Proposed | Rationale |
|---|---|---|
| `core` | `narrative` | The seven fields are narrative slots (subject, trigger, harm, drive, integration, cue, summary); McAdams / Bruner / Pillemer are the homes. |
| `constellation` | `emotion` | The grounded fields are emotion category, blend, body sensation; the narrative and context fields move out. |
| `milky_way` | `context` | Episodic who / where / what. |
| `gravity` | `salience` | Why the memory matters: intensity, tether, cues, persistence, linkage (Conway, Singer & Blagov, Pillemer). |
| `impulse` | `motivation` | Action tendency, need, coping, regulation (Frijda, SDT, Lazarus, Gross). |

Infrastructure domains (`meta`, `governance`, `telemetry`, `system`, `crosswalks`, `extensions`) are untouched.

## Field-by-field mapping

Action: **rename** (same semantics, new name/domain), **move** (semantics unchanged, different domain), **merge** (folded into another field), **cut** (removed), **new**. "Term source" names the framework whose own term the new name follows.

| # | v0.8.3 field | Proposed field | Action | Term source |
|---|---|---|---|---|
| 1 | `core.anchor` | `narrative.subject` | rename | EmotionML `reference@targetedAt`; OCC object |
| 2 | `core.spark` | `narrative.trigger` | rename | EmotionML `reference@triggeredBy` |
| 3 | `core.wound` | `narrative.harm` | rename | Lazarus & Folkman harm/loss appraisal; MFOEM appraisal of loss |
| 4 | `core.fuel` | `narrative.drive` | rename | Panksepp SEEKING; SDT intrinsic motivation |
| 5 | `core.bridge` | `narrative.integration` | rename | Singer & Blagov integrative meaning |
| 6 | `core.echo` | `salience.retrieval_cues` | merge | Tulving retrieval cue (encoding specificity) |
| 7 | `core.narrative` | `narrative.summary` | rename | as requested |
| 8 | `constellation.emotion_primary` | `emotion.primary` | rename | EmotionML `<category>` |
| 9 | `constellation.emotion_subtone` | `emotion.secondary` | rename | EmotionML multiple categories; EARL complex-emotion |
| 10 | `constellation.higher_order_emotion` | `emotion.secondary` | merge | Cowen & Keltner (awe, nostalgia are ordinary categories) |
| 11 | `constellation.meta_emotional_state` | `emotion.meta` | rename | meta-emotion (Gottman et al. 1996) [KNOWLEDGE] |
| 12 | `constellation.interpersonal_affect` | — | cut | no framework home beyond EI competencies; extensions if wanted |
| 13 | `constellation.narrative_arc` | `narrative.arc` | merge (with 26) | Booker / McAdams |
| 14 | `constellation.relational_dynamics` | `context.relationship` | move (dedupe) | Fiske relational models as companion code |
| 15 | `constellation.temporal_context` | `context.life_stage` | move | Conway lifetime period |
| 16 | `constellation.memory_type` | `salience.memory_type` | move (recode) | Pillemer momentous-event types |
| 17 | `constellation.media_format` | — | cut | duplicates `meta.source_type` |
| 18 | `constellation.narrative_archetype` | `extensions.archetype` | move | Mark & Pearson archetypes [KNOWLEDGE]; not in reference set |
| 19 | `constellation.symbolic_anchor` | `salience.tether` | merge | tether value `symbol` / `object` |
| 20 | `constellation.relational_perspective` | `context.scope` | move | Bronfenbrenner nested systems |
| 21 | `constellation.temporal_rhythm` | `emotion.temporal_profile` | rename (reduce) | EmotionML `<trace>`; Scherer suddenness |
| 22 | `constellation.identity_thread` | `narrative.identity_link` | rename | Conway self-memory system (memory–self linkage) |
| 23 | `constellation.expressed_insight` | `narrative.meaning` | rename | McAdams meaning-making |
| 24 | `constellation.transformational_pivot` | `narrative.turning_point` | rename | McAdams / Pillemer turning point |
| 25 | `constellation.somatic_signature` | `emotion.bodily_sensation` | rename | GRID bodily reactions; MFOEM physiological process involved in an emotion |
| 26 | `constellation.arc_type` | `narrative.arc` | move | Booker / Campbell / McAdams |
| 27 | `milky_way.event_type` | `context.event` | rename | Singer & Blagov content category as companion |
| 28 | `milky_way.location_context` | `context.place` | rename | Tulving episodic "where" |
| 29 | `milky_way.associated_people` | `context.people` | rename | — |
| 30 | `milky_way.visibility_context` | — | cut | duplicates `meta.visibility` |
| 31 | `milky_way.tone_shift` | `narrative.valence_shift` | rename | McAdams redemption / contamination sequence |
| 32 | `gravity.emotional_weight` | `emotion.intensity` | move | EmotionML intensity dimension; Plutchik intensity |
| 33 | `gravity.emotional_density` | — | cut | no framework construct |
| 34 | `gravity.valence` | `emotion.valence` | move | Russell; PAD; MFOEM valence |
| 35 | `gravity.viscosity` | `salience.persistence` | merge (with 43) | affective chronometry (Davidson 1998) [KNOWLEDGE]; MFOEM mood vs emotion |
| 36 | `gravity.gravity_type` | `salience.tether` | merge | Lazarus ego-involvement types |
| 37 | `gravity.tether_type` | `salience.tether` | rename | OCC agents / events / objects |
| 38 | `gravity.recall_triggers` | `salience.retrieval_cues` | rename | Tulving; Conway sensory-perceptual cue |
| 39 | `gravity.retrieval_keys` | `salience.retrieval_cues` | merge | Tulving retrieval cue |
| 40 | `gravity.nearby_themes` | `salience.themes` | rename | Conway thematic linkage |
| 41 | `gravity.recurrence_pattern` | `salience.recurrence` | rename | Singer & Blagov specificity |
| 42 | `gravity.strength_score` | `salience.linkage_strength` | rename | SDM criterion "linked to similar memories" |
| 43 | `gravity.temporal_decay` | `salience.persistence` | merge | see 35 |
| 44 | `gravity.resilience_markers` | `salience.resilience` | rename | Lazarus positive reappraisal; Bar-On optimism |
| 45 | `gravity.adaptation_trajectory` | `salience.trajectory` | rename | McAdams redemption / contamination |
| 46 | `impulse.primary_energy` | — | cut | duplicates `emotion.primary` |
| 47 | `impulse.drive_state` | `motivation.action_tendency` | rename | Frijda action tendency (EmotionML vocabulary) |
| 48 | `impulse.motivational_orientation` | `motivation.need` | rename | SDT basic psychological needs |
| 49 | `impulse.temporal_focus` | `motivation.temporal_focus` | rename | Tulving chronesthesia |
| 50 | `impulse.directionality` | `context.scope` | merge | Bronfenbrenner |
| 51 | `impulse.social_visibility` | — | cut | duplicates `context.scope` and `meta.visibility` |
| 52 | `impulse.urgency` | `emotion.appraisal.urgency` | move | Scherer urgency check; EmotionML `ema-appraisals#urgency` |
| 53 | `impulse.risk_posture` | `motivation.risk_posture` | rename | Lazarus threat / challenge |
| 54 | `impulse.agency_level` | `emotion.appraisal.control` | move | Scherer coping potential (control, power); EmotionML `controllability` |
| 55 | `impulse.regulation_state` | `motivation.regulation_state` | rename | Gross emotion regulation |
| 56 | `impulse.attachment_style` | `motivation.attachment_style` | rename | Ainsworth / Main |
| 57 | `impulse.coping_style` | `motivation.coping` | rename | Lazarus & Folkman Ways of Coping |
| — | (new) | `emotion.kind` | new | MFOEM emotion / mood / feeling / disposition |
| — | (new) | `emotion.arousal` | new | Russell; PAD; GRID; EmotionML `pad-dimensions#arousal` |
| — | (new) | `emotion.appraisal.attribution` | new | Scherer agent-self / other / nature; MFOEM appraisal of causal agency |
| — | (new) | `context.event_category` | new | Singer & Blagov / Thorne & McLean content categories |
| — | (new) | `context.relationship_model` | new | Fiske relational models |
| — | (new) | `salience.function` | new | Pillemer / Bluck memory functions (directive, self, social) |
| — | (new, infrastructure) | `telemetry.field_confidence` | new | EmotionML `confidence` attribute |

Tally: 57 old fields → 7 cut, 8 merged into others, 42 carried (renamed or moved), 6 new affective fields → **48 affective fields** in the proposed v0.9 (plus one telemetry field). The one-page v0.9 list is in `REPORT.md`.

## Value-level renames worth making at the same time

| Field | Old value | New value | Reason |
|---|---|---|---|
| `emotion.primary` | wonder | awe (keep wonder as text) | Cowen & Keltner, Hume, Plutchik dyad all code awe |
| `emotion.primary` | peace | serenity / calmness | MFOEM:000043, Plutchik, Cowen & Keltner, Hume, EARL |
| `emotion.primary` | tenderness | love / compassion | MFOEM:000048 / MFOEM:000052, GRID, OCC |
| `emotion.primary` | longing | nostalgia (keep longing as text) | Cowen & Keltner, Hume, Anthropic 171 |
| `motivation.need` | belonging / mastery | relatedness / competence | SDT's own terms |
| `motivation.action_tendency` | explore / share / confront / protect | attending / being-with / agonistic / dominating | Frijda vocabulary (only if the Frijda coding is primary; otherwise keep the EDM words as text and code them) |
| `motivation.coping` | detach / reframe_meaning / seek_support / confront | distancing / positive_reappraisal / seeking_social_support / confrontive_coping | Ways of Coping scale names |
| `salience.memory_type` | formative_experience / milestone | originating_event / turning_point | Pillemer |
| `context.relationship` | friend, couple, grief, self_reflection | drop (friend=friendship, couple=romantic_partnership; grief and self_reflection are not relationships) | dedupe |

Recommendation: keep the EDM value words as the `text` the extractor writes (they are what the prompt vocabulary uses) and apply the framework terms as codes, so no artifact text has to change in migration.
