# Can EDM v0.8.3 become a complete, generic affective ontology? — Discovery report

Date: 2026-10-17. Branch: `discovery/ontology-crosswalk`. Scope: the five affective domains of EDM v0.8.3 (`core`, `constellation`, `milky_way`, `gravity`, `impulse`; 57 fields, 185 canonical values) mapped onto 39 frameworks. Nothing normative was changed. Every number below is reproduced in `crosswalk_stats.json`; every citation is in `frameworks.json`; unverified claims are tagged [KNOWLEDGE] and listed in §9.

## 1. Answer in brief

**Yes, with a reorganisation rather than a rewrite.** Almost every EDM field touches an established construct (98% of fields and 85% of canonical values have at least one mapping), but only a third are *exactly* the construct a framework names (33% of fields, 34% of values). The rest are EDM paraphrases of ideas that exist elsewhere under other names, duplicates of each other, or genuinely EDM-specific. Concretely:

- **Adopt existing codes** for the emotion category (MFOEM, EmotionML vocabularies), the dimensions (EmotionML / PAD / GRID), action tendencies (Frijda via EmotionML), coping (Lazarus & Folkman), attachment (Ainsworth/Main) and needs (SDT). These cover 19 fields today and would cover 28 after the merges in `naming-proposal.md`.
- **Keep as EDM-specific** eleven constructs that no listed framework covers (ritual/tradition tethers, phenomenological temporal profile, meta-emotion, religious coping, persistence, network linkage strength, and the narrative slot set harm/drive/integration). These are the candidates for the ontology experiment (§7).
- **Cut or merge** 15 fields that are duplicates, governance leakage, or marketing-derived (`narrative_archetype`), and 15 canonical values (§5).
- **Add** six fields the frameworks consider essential and EDM lacks: arousal, emotion kind (emotion/mood/feeling), causal attribution, memory function, event category, relationship model (§4).

Net: 57 fields → 48, with every categorical field carrying `text + codings` (see `coding-proposal.md`) so that EDM asserts interpretations, not theories (see `theoretical-conflicts.md`).

## 2. Method and reference set

1. `fields.json`: machine inventory of the five fragments and the three composite schemas (57 fields: 22 closed enums, 7 canonical-open lists, 19 free text, 6 lists, 2 numeric, 1 boolean; 3 of the 57 are administrative, not affective).
2. `frameworks.json`: 39 frameworks in six families, extracted by four parallel research passes plus a direct download of the MFOEM OWL (version 2025-07-31; 223 non-deprecated MFOEM classes, 63 emotion-process subclasses) and a direct extraction of the Anthropic 2026 appendix (171 emotion words, count verified).

| Source status | Frameworks |
|---|---|
| FETCHED (primary/official page read) | 14 — Ekman, Cowen & Keltner, GoEmotions, Barrett, Anthropic 2026, Hume, SDT, Goleman/Boyatzis, Bar-On, EmotionML + vocabularies, WordNet-Affect, NRC, SenticNet, MFOEM |
| FETCHED_SECONDARY (official abstract / distributor / archive / encyclopedia; some values from knowledge) | 20 — Plutchik, Russell, PAD, Scherer/GRID/GEW, Panksepp, Damasio, Conway, Singer & Blagov, Pillemer, Lazarus, McAdams, Bruner, Booker, Campbell, Tulving, Ainsworth, Bartholomew, Fiske, HUMAINE EARL, SNOMED CT |
| KNOWLEDGE (no fetch succeeded) | 5 — OCC (0.9), Bronfenbrenner (0.92), Gross (0.95), Elliot (0.93), Mayer–Salovey (0.95) |

3. `crosswalk.csv` / `crosswalk.md`: 242 rows × 39 columns, 913 mappings, relations exact / broader / narrower / related. Each target label was checked automatically against the extracted value lists: **393 verified against fetched lists (V), 241 found only in knowledge-reconstructed lists (K), 279 free-form structural targets not checkable (-)**.

Limits: the matrix was authored by one pass and then verified; relation judgements (exact vs related) are mine, not the frameworks'. SNOMED codes were verified on the HL7 terminology server because the official browser blocks automated clients. HUMAINE EARL came from a 2008 Internet Archive snapshot. Publisher pages (APA, Wiley, Springer, T&F) returned 403 throughout, which is why most classic psychology sources are FETCHED_SECONDARY.

## 3. How much of EDM is grounded

| Level | Any mapping | Exact mapping | Related-only | Orphan |
|---|---|---|---|---|
| Fields (57) | 98.2% (56) | 33.3% (19) | 63.2% (36) | 1 (`visibility_context`) |
| Affective fields (54) | 100% | 35.2% (19) | 63.0% (34) | 0 |
| Canonical values (185) | 85.4% (158) | 33.5% (62) | 51.9% (96) | 14.6% (27) |

By domain (fields exact / fields total; values exact / values total):

| Domain | Fields exact | Values exact | Reading |
|---|---|---|---|
| core | 1 / 7 | — | narrative slots; only `spark` has an exact home (EmotionML triggeredBy) |
| constellation | 6 / 19 | 31 / 102 | emotion labels and insight/turning-point fields are grounded; arcs, archetypes, rhythms are not |
| milky_way | 1 / 5 | 0 / 3 | episodic context; `tone_shift` = McAdams redemption/contamination |
| gravity | 4 / 14 | 7 / 32 | intensity, valence, retrieval cues grounded; persistence, density, tether not |
| impulse | 7 / 12 | 24 / 48 | best-grounded domain: action tendency, needs, urgency, control, attachment, coping |

The 19 exactly-grounded fields: `core.spark`, `emotion_primary`, `emotion_subtone`, `identity_thread`, `expressed_insight`, `transformational_pivot`, `somatic_signature`, `tone_shift`, `emotional_weight`, `valence`, `recall_triggers`, `retrieval_keys`, `drive_state`, `motivational_orientation`, `temporal_focus`, `urgency`, `agency_level`, `attachment_style`, `coping_style`.

Framework reach (rows touched / exact): McAdams 82/7, Lazarus 58/20, MFOEM 57/25, EmotionML 54/23, Conway 38/3, Singer & Blagov 36/7, Panksepp 36/5. The emotion category value set is reached by 20 frameworks; the narrative and salience fields by five or six each; the EI frameworks (Mayer–Salovey, Goleman, Bar-On) touch nothing exactly and are person-level (see conflicts §5).

## 4. What is uniquely EDM

Strict orphans (no mapping at all): 1 field and 27 values. Removing scale midpoints (medium, balanced, wavering, moderate, stable) and the governance field, the substantive orphans are:

| Construct | Decision | Why no framework covers it |
|---|---|---|
| `tether_type = ritual, tradition` | keep | Collective / commemorative memory (Halbwachs 1925; Connerton 1989) [KNOWLEDGE] is outside the individual-level reference set |
| `temporal_rhythm = spiraling, dragging, suspended` | keep | Phenomenological time of affect (Fuchs 2013; Minkowski) [KNOWLEDGE]; EmotionML `<trace>` cannot express shape |
| `coping_style = ritualize` | keep | Religious/spiritual coping (Pargament RCOPE) [KNOWLEDGE] is not in Ways of Coping or Gross |
| `memory_type = legacy_artifact` | merge | A tether (object), not a memory type |
| `narrative_archetype` (6 orphan values, 12 total) | cut → extensions | Mark & Pearson 2001 brand archetypes [KNOWLEDGE]; nearest academic construct is McAdams imagoes |
| `viscosity = fluid`, `recurrence_pattern = emerging`, `adaptation_trajectory = emerging`, `emotional_density = medium` | cut | nominal values inside ordinal scales, or duplicates |

Related-only fields that are nevertheless EDM-specific as *fields* (the idea exists, the slot does not): `strength_score` (network linkage), `viscosity`/`temporal_decay` (persistence), `meta_emotional_state`, `gravity_type`, and the narrative slot set `wound`/`fuel`/`bridge`. Decisions for all 36 related-only fields are in `crosswalk.md` Gap list A2 (22 keep, 6 cut, 8 merge).

## 5. What would be added, what would be cut

**Add (15 gap decisions, consolidated to 6 fields + 1 infrastructure field):**

| New field | Source | Why |
|---|---|---|
| `emotion.arousal` | Russell, PAD, GRID, Barrett, NRC VAD, EmotionML `pad-dimensions#arousal` | The second axis of every dimensional model has no EDM home |
| `emotion.kind` (emotion / mood / feeling / disposition) | MFOEM `000001 / 000193 / 000006 / 000199`; Damasio | EDM cannot say whether "peace" was an emotion or a mood |
| `emotion.appraisal.attribution` (self / other / chance) | Scherer agent-self/other/nature; Lazarus blame/credit; MFOEM `000075–000084` | Stated attributions ("I blamed myself") have nowhere to go |
| `salience.function` (directive / self / social) | Pillemer 1992; Bluck 2003 | The best-attested answer to "why does this memory matter" |
| `context.event_category` | Singer & Blagov / Thorne & McLean content categories | Coded companion to free-text `event_type` |
| `context.relationship_model` | Fiske 1992 | Coded companion to `relational_dynamics` |
| `telemetry.field_confidence` | EmotionML `confidence` attribute | Every EmotionML annotation carries confidence; EDM has none |

Also added as *codes* rather than fields: disgust, surprise, contempt, guilt, interest, awe, love, nostalgia, loneliness, grief, regret, embarrassment, envy, boredom, amusement, contentment, compassion, trust — i.e. the MFOEM emotion-process list replaces the canonical 17 as the recommended vocabulary (the field already accepts free text, so this is additive).

**Cut (7 fields):** `interpersonal_affect`, `media_format`, `visibility_context`, `emotional_density`, `primary_energy`, `social_visibility`, `narrative_archetype` (moved to extensions). **Merge (8 fields):** `echo` and `retrieval_keys` → `retrieval_cues`; `higher_order_emotion` → `secondary`; `narrative_arc` → `arc`; `symbolic_anchor` and `gravity_type` → `tether`; `temporal_decay` → `persistence`; `directionality` → `scope`. **Cut (values):** 15, listed in Gap list A.

**Out of scope by design (16 gap decisions):** motor expression, person-level traits (EI competencies, granularity, attachment dimensions), SDT motivation continuum, Bruner's narrative features, clinical mood codes in the affective core, third-party experiencers. Each has a reason in Gap list B.

## 6. Proposed v0.9 domain / field list (one page)

48 affective fields. Codes in brackets name the primary coding system from `coding-proposal.md`; ★ = new; † = EDM-specific (no external code).

**narrative** (11): `subject`, `trigger` [EmotionML triggeredBy], `harm` [Lazarus harm/loss] †, `drive` †, `integration` [Singer integrative meaning] †, `summary`, `meaning` [McAdams meaning-making], `identity_link` [Conway], `turning_point` [McAdams/Pillemer], `arc` [EDM vocab ↔ Booker/Campbell/McAdams], `valence_shift` [McAdams redemption/contamination]

**emotion** (12): `primary` [MFOEM], `secondary[]` [MFOEM], `kind` ★ [MFOEM], `valence` [EmotionML/MFOEM], `arousal` ★ [EmotionML], `intensity` [EmotionML], `meta` †, `bodily_sensation` [MFOEM physiological process], `temporal_profile` [EmotionML trace + EDM †], `appraisal.urgency` [EmotionML/MFOEM], `appraisal.control` [EmotionML/Scherer], `appraisal.attribution` ★ [MFOEM/Scherer]

**context** (8): `event`, `event_category` ★ [Singer & Blagov], `place`, `people`, `relationship` [EDM vocab], `relationship_model` ★ [Fiske], `life_stage` [Conway], `scope` [Bronfenbrenner]

**salience** (10): `memory_type` [Pillemer], `tether` [EDM vocab ↔ OCC; ritual/tradition †], `retrieval_cues` [Tulving], `themes` [Conway], `recurrence` [Singer specificity], `persistence` †, `linkage_strength` †, `function` ★ [Pillemer/Bluck], `resilience` [Lazarus/Bar-On], `trajectory` [McAdams]

**motivation** (7): `action_tendency` [Frijda via EmotionML], `need` [SDT], `temporal_focus` [Tulving], `risk_posture` [Lazarus threat/challenge], `regulation_state` [Gross] , `attachment_style` [Ainsworth/Main], `coping` [Ways of Coping + Gross]

Profiles would follow the same tiering as today (Essential ≈ narrative + emotion.primary/secondary/valence/intensity; Extended adds context and salience; Full adds motivation and appraisal). Field counts per profile are not proposed here.

## 7. Uniquely-EDM constructs ranked for the ontology experiment

Ranking = how often the construct appears in the memory/significance literature in the reference set (count of *related* mappings in the matrix) plus adjacent literature not in the set [KNOWLEDGE]. Higher rank = more worth testing because a framework nearly has it.

| Rank | Construct | Related mappings in matrix | Adjacent literature | Experiment question |
|---|---|---|---|---|
| 1 | `wound` / `fuel` / `bridge` narrative slot set | 7 / 6 / 4 | Lazarus harm-loss; Panksepp SEEKING; Singer integrative meaning | Do raters reproduce the three slots more reliably than McAdams agency/communion? |
| 2 | `meta_emotional_state` | 4 (Gross, Mayer–Salovey, Goleman, Bar-On) | Gottman meta-emotion; Mitmansgruber [KNOWLEDGE] | Is stated meta-emotion extractable without inference? |
| 3 | `viscosity` + `temporal_decay` (persistence) | 4 + 4 | Davidson affective chronometry [KNOWLEDGE]; MFOEM mood/emotion | Does a stated-persistence ordinal predict recall at re-capture? |
| 4 | `gravity_type` / tether as self-relevance | 3 | Lazarus ego-involvement types; Conway self-relevance | Does tether type separate self-defining from ordinary memories (Singer criteria)? |
| 5 | `strength_score` (network linkage) | 2 (Conway, Singer "linked to similar memories") | — | Can linkage be scored from stated content alone? |
| 6 | `tether_type = ritual / tradition` | 0 | Halbwachs; Connerton [KNOWLEDGE] | Frequency in journaling/wiki corpora; does it co-occur with recurrence=cyclical? |
| 7 | `temporal_rhythm = spiraling / dragging / suspended` | 0 | Fuchs; Minkowski [KNOWLEDGE] | Inter-rater agreement vs a reduced still/sudden/rising/fading set |
| 8 | `coping_style = ritualize` | 0 | Pargament RCOPE [KNOWLEDGE] | Frequency; collapse into reframe_meaning or keep? |
| 9 | `emotional_density` | 4 (weak) | — | Expected to be redundant with secondary[] cardinality: test and cut |
| 10 | `narrative_archetype` | 2 (McAdams imagoes, Campbell hero) | Mark & Pearson [KNOWLEDGE] | Expected not to replicate as identity coding; test before deciding extensions vs removal |
| 11 | `social_visibility` / `directionality` | 1 / 3 | — | Duplicates; no test needed |

## 8. Theoretical neutrality (summary of `theoretical-conflicts.md`)

Eleven conflicts were identified (basic vs constructed emotion, discrete vs dimensional, appraisal vs affect-program, emotion/mood/feeling, event vs person level, literary vs empirical narrative, memory taxonomies, gradient vs list, coping vs regulation, LLM functional concepts, collective vs individual memory). The single mechanism that keeps EDM neutral in all of them is `text + codings` with an explicit `relation` per coding and the rule that codes never replace the subject's words. This is already EDM's "interpretation only" constraint, made machine-readable.

## 9. Unverified claims register

Everything tagged [KNOWLEDGE] in the deliverables is one of:

- **Whole frameworks reconstructed from knowledge** (no fetch): OCC 22 types and branches; Gross five families, ERQ, extended model; Elliot 2×2 and temperaments; Mayer–Salovey four branches / MSCEIT; Bronfenbrenner five systems / PPCT.
- **Value lists reconstructed from knowledge inside otherwise-fetched frameworks**: Plutchik 24 intensity terms and dyads; Russell 28 words and octants; PAD octant labels; GRID 24 terms, GEW 20 families and the SEC list; Ekman's 1999 expanded list; Panksepp ANPS scales; Damasio classes and self levels; Conway hierarchy, retrieval modes and SDM criteria; Singer & Blagov category labels; Pillemer five features and four event types; McAdams coded constructs, themes, nuclear episodes and imagoes; Bruner ten features and dual landscape; Tulving consciousness kinds; Ainsworth subgroups and Main & Solomon D; Bartholomew four prototypes; WordNet-Affect six Ekman classes; Goleman competency-to-domain grouping; SDT six-point continuum.
- **Literature cited outside the reference set** (never fetched): Mark & Pearson 2001; Fuchs 2013; Minkowski; Halbwachs 1925; Connerton 1989; Pargament 1997/2000; Davidson 1998; Gottman et al. 1996; Mitmansgruber et al. 2009; Keltner & Haidt 2003; Sedikides & Wildschut; Leary 1957; Erikson; Bonanno; Thorne & McLean; Bluck 2003; HL7 FHIR Coding; W3C SKOS.
- **Known source problems**: Cowen & Keltner 2017 is internally inconsistent about pride vs relief in the 27; Hume's current docs no longer publish the 48/53 per-modality lists in the form the literature cites; EmotionML `occ-appraisals` shows `realization` in the HTML Note but not in the automated XML read; HUMAINE EARL is from an archive snapshot; SNOMED codes were verified on tx.fhir.org, not on the SNOMED browser.

## 10. Recommended next steps

1. Decide the five domain renames and the 15 cuts/merges first; they are independent of any coding system.
2. File new-term requests with the MFOEM maintainers for awe, gratitude, relief, longing/nostalgia, tenderness, frustration; EDM's emotion list is the only place these seven are uncoded.
3. Run the ontology experiment on ranks 1–5 of §7 before deciding whether EDM-specific fields survive v0.9.
4. Publish the EDM vocabularies (`arc`, `tether`, `relationship`, `memory_type`, `temporal_profile`, `need`, `coping`) as SKOS with the crosswalk relations from `crosswalk.csv` as `skos:*Match` triples.
