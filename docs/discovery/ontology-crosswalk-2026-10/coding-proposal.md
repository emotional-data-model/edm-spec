# Coding proposal — EDM categorical fields as code + system + version + text

Discovery output, 2026-10-17. Nothing here is normative. Companion to `crosswalk.md` (mappings) and `frameworks.json` (sources).

## Pattern

Every categorical field keeps the subject's own words (`text`) and carries zero or more `codings`, each naming the code system and the version it was drawn from. The shape is HL7 FHIR R4 `CodeableConcept` / `Coding` (`system`, `version`, `code`, `display`) [FETCHED-adjacent: FHIR R4 datatypes, https://hl7.org/fhir/R4/datatypes.html#Coding — not in the reference set, cited as the pattern only]. EmotionML uses the same separation: a `<category name>` is meaningful only relative to a `category-set` URI (W3C EmotionML 1.0 §2.1; vocabularies Note 2014-04-01, see `frameworks.json#emotionml`).

```json
"primary": {
  "text": "joy",
  "codings": [
    {"system": "http://purl.obolibrary.org/obo/mfoem.owl", "version": "2025-07-31", "code": "MFOEM:000034", "display": "joy"},
    {"system": "http://www.w3.org/TR/emotion-voc/xml#fsre-categories", "version": "2014-04-01", "code": "joy", "display": "joy"},
    {"system": "http://snomed.info/sct", "version": "http://snomed.info/sct/900000000000207008/version/20250201", "code": "112080002", "display": "Cheerful mood (finding)", "relation": "related"}
  ]
}
```

Rules proposed for v0.9:

1. `text` is mandatory and is the interpretation. `codings` are optional, additive and may disagree with each other; a coding never replaces the text.
2. A coding may carry `relation` (`exact` default | `broader` | `narrower` | `related`) when the code is not an exact match, using the same four relations as the crosswalk.
3. One primary system per field is recommended below so that validators and the registry have a default; other systems live in `crosswalks` or in additional codings.
4. Where EDM's canonical list is finer than the best system, the EDM value is itself published as a code in an EDM-owned vocabulary (`https://emotionaldatamodel.org/vocab/<field>/v1#<value>`; **proposed, does not exist yet**), with `skos:broadMatch` / `skos:closeMatch` links to the external system. SKOS mapping properties are the standard way to express exact/broader/narrower/related between vocabularies [KNOWLEDGE: W3C SKOS Reference 2009, §10 — not fetched].

## Recommendation by field

Columns: primary system (preferred), secondary systems, and whether EDM's canonical list is **finer**, **coarser**, or **different** in kind from the best system. Versions are those verified in `frameworks.json`.

| EDM field (v0.8.3) | Primary coding system (version) | Secondary / fallback | EDM list vs best system |
|---|---|---|---|
| `constellation.emotion_primary` | **MFOEM** emotion process subclasses (2025-07-31): 10 of 17 values exact (joy, sadness, fear, anger, pride, anxiety, hope, shame, disappointment; peace→serenity) | EmotionML `fsre-categories` / `occ-categories` (2014-04-01) cover gratitude, relief; HUMAINE EARL 48 covers 13/17; GoEmotions (2020) 13/17; SNOMED CT 20250201 10/17 (see list below) | **finer than Ekman (6/7), coarser than MFOEM (63) and GoEmotions (27)**. 7 values have no MFOEM class: wonder, tenderness, reverence, gratitude, longing, relief, frustration. Proposal: file new-term requests upstream (awe, gratitude, relief, longing, tenderness, frustration) and in the meantime code them with `relation: related` to the nearest class. |
| `constellation.emotion_subtone` | same as primary, array | EmotionML multiple `<category>` with `confidence`; EARL `<complex-emotion>` | n/a (free text) |
| `constellation.narrative_arc` + `arc_type` | EDM vocab `arc/v1` (proposed) with per-value `closeMatch` to Booker (2004) plots, Campbell (1949) stages, McAdams (2001) redemption/contamination | none machine-readable | **finer** than Booker (7); **different in kind** from Campbell (stage sequence). Merge the two fields first (transformation appears in both). |
| `constellation.relational_dynamics` | EDM vocab `relationship/v1` (proposed), deduplicated (friend=friendship, couple=romantic_partnership; drop grief, self_reflection) | companion code: Fiske (1992) relational model — communal_sharing / authority_ranking / equality_matching / market_pricing / null | **finer** than Fiske (4); Fiske is a model, EDM is a role type: keep both |
| `constellation.temporal_context` | EDM vocab `life_stage/v1` | Conway lifetime period (thematic; no code list) | no coded system; **different in kind** from Conway |
| `constellation.memory_type` | EDM vocab `memory_type/v1` recoded to Pillemer (2001) event types: originating_event, turning_point, anchoring_event, analogous_event + event_specific (Conway ESK) | Singer & Blagov self-defining memory as boolean flag | **different in kind**; current values (legacy_artifact, fleeting_moment, milestone, reflection, formative_experience) are only partially Pillemer |
| `constellation.media_format` | cut: duplicate of `meta.source_type` | — | — |
| `constellation.narrative_archetype` | move to EXTENSIONS as `archetype/v1` (12 values, Mark & Pearson 2001 [KNOWLEDGE]) | McAdams imagoes (open list) | **different in kind**; no academic coded system |
| `constellation.relational_perspective` | EDM vocab `scope/v1`: self, dyad, microsystem, mesosystem, macrosystem (Bronfenbrenner 1979; verified 2026-10-17 against Tong & An 2024, Frontiers) | — | **coarser/renamed**: partner/family/friends collapse to microsystem unless kept as sub-codes |
| `constellation.temporal_rhythm` | EDM vocab `temporal_profile/v1`: still, sudden, rising, fading, recurring (+ spiraling, dragging, suspended as EDM-specific) | EmotionML `scherer-appraisals#suddenness` for sudden; `<trace>` for rising/fading | **different in kind**; EmotionML can only encode intensity-over-time, not shape qualities |
| `gravity.valence` | EmotionML `fsre-dimensions#valence` or `pad-dimensions#pleasure` as a numeric dimension; categorical: MFOEM `MFOEM:000207` positive valence / `MFOEM:000208` negative valence | NRC VAD valence (v2.1, 2025); WordNet-Affect positive/negative/ambiguous; GoEmotions sentiment | EDM `mixed` is **finer** than MFOEM (no mixed class) and equals WordNet-Affect/GoEmotions `ambiguous` |
| `gravity.emotional_density` | cut | — | — |
| `gravity.viscosity`, `gravity.temporal_decay` | merge into `salience.persistence` ordinal (transient, short, enduring, chronic); EDM vocab | EmotionML `duration` attribute (numeric) | no coded system; **different in kind** (prediction vs measurement) |
| `gravity.tether_type` | EDM vocab `tether/v1`; person/event/object `closeMatch` to OCC branches agents/events/objects (Ortony et al. 1988; verified 2026-10-17 against Adam, Herzig & Longin 2009 and Clore & Ortony 2013) | EmotionML `<reference role="targetedAt">` with a URI for the tether | **finer** (adds symbol, place, ritual, tradition, identity, self) |
| `gravity.recurrence_pattern` | EDM vocab `recurrence/v1`: isolated, repeated, chronic (drop emerging) | companion: Singer & Blagov specificity specific / summary | **different in kind** |
| `gravity.adaptation_trajectory` | EDM vocab `trajectory/v1`: improving, stable, declining, integrative; `closeMatch` McAdams redemption / contamination / coherent positive resolution | — | **finer** than McAdams (2 directions + resolution) |
| `impulse.drive_state` | EmotionML `frijda-action-tendencies` (2014-04-01): approach, avoidance, being-with (share), attending (explore), agonistic (confront), dominating (protect) | MFOEM `MFOEM:000007` emotional action tendency; `MFOEM:000136`/`000137` moving towards/away from people; Plutchik adaptive behaviours | **different**: repair, persevere, process have no Frijda tendency; keep as EDM codes |
| `impulse.motivational_orientation` | EDM vocab `need/v1`; autonomy / competence(mastery) / relatedness(belonging) `exactMatch` SDT basic needs (selfdeterminationtheory.org, fetched) | — | **finer** than SDT (3): safety, meaning, authenticity are EDM additions |
| `impulse.temporal_focus` | EDM vocab (past, present, future); Tulving chronesthesia as the cited construct | — | no coded system |
| `impulse.directionality`, `impulse.social_visibility` | merge into `context.scope` / cut | — | — |
| `impulse.urgency` | EmotionML `ema-appraisals#urgency` / `scherer-appraisals#urgency` (numeric 0..1); EDM 4-level ordinal maps to quartiles | MFOEM `MFOEM:000089` appraisal as urgent / `MFOEM:000090` not urgent | **finer** than MFOEM (binary); **coarser** than EmotionML (continuous) |
| `impulse.risk_posture` | EDM vocab; cautious/bold `closeMatch` Lazarus threat / challenge appraisal | — | no coded system |
| `impulse.agency_level` | EmotionML `pad-dimensions#dominance` / `scherer-appraisals#control` + `#power` (numeric) | MFOEM `MFOEM:000110` feeling in control / `MFOEM:000116` feeling out of control; NRC VAD dominance | **coarser** than EmotionML (3 levels vs continuous) |
| `impulse.regulation_state` | EDM vocab; `related` SNOMED emotional-state findings only if a clinical profile needs them | Gross (1998) names strategies, not states | no coded system |
| `impulse.attachment_style` | EDM vocab with Ainsworth/Main letter codes as `display` (A avoidant, B secure, C anxious-ambivalent, D disorganized) | Bartholomew & Horowitz 1991 four prototypes (`related`) | **exact** to Ainsworth + Main & Solomon [Main & Solomon D verified 2026-10-17 against Granqvist et al. 2017, PMC5600694] |
| `impulse.coping_style` | Lazarus & Folkman Ways of Coping scales (Mind Garden, fetched): reframe_meaning→Positive Reappraisal, seek_support→Seeking Social Support, confront→Confrontive Coping, detach→Distancing, distract→Escape-Avoidance (related) | Gross process-model family as a second coding (cognitive change, attentional deployment, ...) | **different**: ritualize and process have no WCQ scale; keep as EDM codes |
| `milky_way.visibility_context` | cut (governance) | — | — |

### SNOMED CT codes available for the 17 emotion values (verified on tx.fhir.org, International Edition 20250201)

| EDM value | SCTID | FSN | Relation |
|---|---|---|---|
| joy | 112080002 | Cheerful mood (finding) (synonym Happiness) | related |
| sadness | 420038007 | Feeling unhappy (finding) | exact |
| fear | 1402001 | Fear (finding) | exact |
| anger | 75408008 | Feeling angry (finding) | exact |
| wonder | — | none | — |
| peace | 102894008 | Feeling calm (finding) | related |
| tenderness | 23682002 | Love (finding) | related |
| reverence | — | none | — |
| pride | 1149081002 | Feeling proud (finding) | exact |
| anxiety | 48694002 | Anxiety (finding) | exact |
| gratitude | — | none | — |
| longing | — | none | — |
| hope | 225649001 | Hopeful for the future (finding) | exact |
| shame | 225012006 | Feeling ashamed (finding) | exact |
| disappointment | — | none | — |
| relief | 224978009 | Feeling relief (finding) | exact |
| frustration | 224973000 | Feeling frustrated (finding) | exact |

SNOMED CT use requires an Affiliate Licence outside Member territories; keep SNOMED codings in `crosswalks`, not in the affective core.

## Fields that should become dimensions rather than categories

`gravity.emotional_weight` (0..1) is already dimension-shaped and maps exactly to EmotionML `intensity-dimension`; `gravity.valence`, `impulse.urgency` and `impulse.agency_level` have continuous homes (EmotionML `pad-dimensions`, `fsre-dimensions`, `ema-appraisals`, NRC VAD). Proposal: allow a numeric `value` next to the ordinal `text` for these four, so a dimensional consumer reads the number and a categorical consumer reads the label.

## Where EDM is finer or coarser than the best available system (summary)

| Field | Best system | Size | EDM size | Verdict |
|---|---|---|---|---|
| emotion_primary | MFOEM emotion process | 63 classes | 17 | coarser; 7 EDM values missing upstream |
| emotion_primary | Ekman | 6/7 | 17 | finer |
| arc_type | Booker | 7 | 14 | finer, different axis |
| relational_dynamics | Fiske | 4 (+null) | 19 | finer; EDM is role-typed, Fiske is model-typed |
| drive_state | Frijda action tendencies | 10 | 9 | different (6 overlap) |
| motivational_orientation | SDT needs | 3 | 6 | finer |
| urgency | MFOEM appraisal | 2 | 4 | finer |
| urgency / agency_level | EmotionML appraisal / dimension | continuous | 4 / 3 | coarser |
| valence | MFOEM valence | 2 | 3 (mixed) | finer |
| attachment_style | Ainsworth + Main | 4 | 4 | exact |
| coping_style | Ways of Coping | 8 | 7 | different (5 overlap) |
