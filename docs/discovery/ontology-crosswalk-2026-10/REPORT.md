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
| FETCHED_SECONDARY (official abstract / distributor / archive / encyclopedia / open-access secondary source; construct lists verified against it) | 25 — Plutchik, Russell, PAD, Scherer/GRID/GEW, Panksepp, Damasio, Conway, Singer & Blagov, Pillemer, Lazarus, McAdams, Bruner, Booker, Campbell, Tulving, Ainsworth, Bartholomew, Fiske, HUMAINE EARL, SNOMED CT, and (raised from KNOWLEDGE on 2026-10-17) OCC, Bronfenbrenner, Gross, Elliot, Mayer–Salovey |
| KNOWLEDGE (no fetch succeeded) | 0 — the five frameworks above had every construct list verified against an accessible secondary source; per-construct records are in `frameworks.json` (`constructs[].verified_against`) and `sources/verification_2026-10-17.json` |

3. `crosswalk.csv` / `crosswalk.md`: 242 rows × 39 columns, 913 mappings, relations exact / broader / narrower / related. Each target label was checked automatically against the extracted value lists: **602 verified against fetched or secondary-verified lists (V), 32 found only in knowledge-reconstructed lists (K), 279 free-form structural targets not checkable (-)**. Before the 2026-10-17 verification pass (77 construct lists checked against accessible secondary sources: 70 verified, 4 partial, 2 contradicted, 1 with no list) the split was 393 / 241 / 279.

Limits: the matrix was authored by one pass and then verified; relation judgements (exact vs related) are mine, not the frameworks'. SNOMED codes were verified on the HL7 terminology server because the official browser blocks automated clients. HUMAINE EARL came from a 2008 Internet Archive snapshot. Publisher pages (APA, Wiley, Springer, T&F) returned 403 throughout, which is why most classic psychology sources are FETCHED_SECONDARY. The verification pass therefore relied on open-access reviews (PMC, Frontiers, Psicothema), author or lab sites (unige.ch/cisa, selfdeterminationtheory.org, self-definingmemories.com, Ortony's Northwestern page), university course mirrors of paywalled papers (UVic, UW-Madison, cs.uky.edu, personality-project.org, uvm.edu), one third-party ontology quoting Ekman 1999 verbatim, and Wikipedia for the three Plutchik dyad lists and one Tulving definition; the mirrors' copyright status is their hosts', and they are cited as verification evidence, not as the reference.

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

Superseded on 2026-10-17 by `v0.9-proposal.md` (47 fields: this list minus `attachment_style` and `regulation_state`, which move to an opt-in trait profile, plus `narrative.self_position`). Kept here as the state the crosswalk was built against.

48 affective fields. Codes in brackets name the primary coding system from `coding-proposal.md`; ★ = new; † = EDM-specific (no external code).

**narrative** (11): `subject`, `trigger` [EmotionML triggeredBy], `harm` [Lazarus harm/loss] †, `drive` †, `integration` [Singer integrative meaning] †, `summary`, `meaning` [McAdams meaning-making], `identity_link` [Conway], `turning_point` [McAdams/Pillemer], `arc` [EDM vocab ↔ Booker/Campbell/McAdams], `valence_shift` [McAdams redemption/contamination]

**emotion** (12): `primary` [MFOEM], `secondary[]` [MFOEM], `kind` ★ [MFOEM], `valence` [EmotionML/MFOEM], `arousal` ★ [EmotionML], `intensity` [EmotionML], `meta` †, `bodily_sensation` [MFOEM physiological process], `temporal_profile` [EmotionML trace + EDM †], `appraisal.urgency` [EmotionML/MFOEM], `appraisal.control` [EmotionML/Scherer], `appraisal.attribution` ★ [MFOEM/Scherer]

**context** (8): `event`, `event_category` ★ [Singer & Blagov], `place`, `people`, `relationship` [EDM vocab], `relationship_model` ★ [Fiske], `life_stage` [Conway], `scope` [Bronfenbrenner]

**salience** (10): `memory_type` [Pillemer], `tether` [EDM vocab ↔ OCC; ritual/tradition †], `retrieval_cues` [Tulving], `themes` [Conway], `recurrence` [Singer specificity], `persistence` †, `linkage_strength` †, `function` ★ [Pillemer/Bluck], `resilience` [Lazarus/Bar-On], `trajectory` [McAdams]

**motivation** (7): `action_tendency` [Frijda via EmotionML], `need` [SDT], `temporal_focus` [Tulving], `risk_posture` [Lazarus threat/challenge], `regulation_state` [Gross] , `attachment_style` [Ainsworth/Main], `coping` [Ways of Coping + Gross]

Profiles would follow the same tiering as today (Essential ≈ narrative + emotion.primary/secondary/valence/intensity; Extended adds context and salience; Full adds motivation and appraisal). Field counts per profile are not proposed here.

## 7. Uniquely-EDM constructs ranked for the ontology experiment

The experiment itself is pre-registered in `experiment-plan.md` (50 synthetic texts over the Singer & Blagov categories, 4 models × 5 repeats, per-field repeatability / agreement / null-precision thresholds, and the two downstream tasks: salience-weighted retention and the `self_position` rater study).

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
| 12 | `narrative.self_position` (proposed replacement for `narrative_archetype`; stated-only free text) | 2 (McAdams imagoes; agency / communion) | Hermans dialogical-self I-positions [KNOWLEDGE] | Does a stated self-position change how raters interpret the rest of the record (arc, valence_shift, trajectory, need)? Present the same artifact with and without it. See `v0.9-proposal.md` §3 |

### 7.1 Outcome of the pre-registered run (2026-10-17; `experiments/2026-10-17/RESULTS.md`)

150 texts (synthetic / conversational / Pepys) × 4 extractors (Claude Sonnet 5.5, Claude Haiku 5.5, gpt-6.1-sol, Kimi K2.6) × 5 repeats; frozen thresholds in `experiment-plan.md` §4.1. Pooled outcome per ranked construct:

| Rank | Construct → v0.9 field(s) | Outcome | Evidence |
|---|---|---|---|
| 1 | `wound` / `fuel` / `bridge` → `narrative.harm`, `drive`, `integration` | **harm cut, drive cut; integration pass (null-driven)** | Only Sonnet 5.5 repeats the three slots (0.80–0.88); cross-model equivalence 0.54 / 0.38 / 0.72 (0.40 on populated answers). The slot set does not replicate across models as a comparable record; it survives as an interpretive, model-specific description. |
| 2 | `meta_emotional_state` → `emotion.meta` | **cut** | Repeatable in Sonnet and GPT (0.87 / 0.91), not in Haiku or Kimi (0.74 / 0.72); cross 0.65 (0.34 populated-only); null 63 %. Stated meta-emotion is extractable by the stronger models but not model-independent. |
| 3 | `viscosity` + `temporal_decay` → `salience.persistence` | **cut (text and decay)** | Repeat 0.53–0.86, cross 0.26 / 0.25; the persistence component alone does not beat recency in task (a) pooled (1 of 4 extractors). |
| 4 | `gravity_type` / tether → `salience.tether` | **type pass; referent cut; stake cut** | `tether.type` κ 0.71–0.81 / cross 0.53; `stake` is the least repeatable free-text unit (0.47–0.70, cross 0.33). |
| 5 | `strength_score` → `salience.linkage_strength` | **interpretive** | ICC within model 0.88–0.96 for three extractors; gpt-6.1-sol leaves it null 90 % of the time (ICC 0.09 on the rest); cross ICC 0.50 (borderline). As a task (a) component alone it beats recency pooled (3 of 4). |
| 6 | `tether_type = ritual / tradition` | frequency only | 3.0 % / 0.1 % of outputs; 59 of 91 co-occur with `recurrence = cyclical`. |
| 7 | `temporal_rhythm = spiraling / dragging / suspended` → `emotion.temporal_profile` | **interpretive** | Field κ 0.67–0.80 / cross 0.37; the EDM-specific values appear in 4.4 % (dragging), 2.1 % (suspended), 0.03 % (spiraling) of outputs. |
| 8 | `coping_style = ritualize` → `motivation.coping` | field **pass**; value rare | `coping` κ 0.69–0.82 / cross 0.54; `ritualize` 1.7 % of outputs, `process` 11.9 %. |
| 9 | `emotional_density` | not tested | cut before the run (v0.9 proposal §1). |
| 10 | `narrative_archetype` | replaced | see rank 12. |
| 11 | `social_visibility` / `directionality` → `context.scope.direction` | **cut** | κ 0.60–0.84 / cross 0.37. `scope.text` passes (0.69–0.86 / 0.47). |
| 12 | `narrative.self_position` | field **pass**; task (b) **fail** | Stated-only extraction is highly repeatable (0.90–0.96; cross 0.87, 0.81 populated-only; null 79 %). Restoring it to a blanked artifact shifts 12 % of rater readings of arc / trajectory / need against 9 % for a neutral control field (threshold ≥ 20 % and < 10 %): the field is a legitimate stated-only record, but the claim that it changes downstream interpretation is withdrawn. |

Also decided by the run: `emotion.primary`, `emotion.valence.text`, `emotion.intensity.value`, `emotion.appraisal.attribution`, `emotion.bodily_sensation`, `context.event_category`, `context.relationship`, `salience.function`, `motivation.action_tendency / need / temporal_focus / coping`, `narrative.turning_point`, `narrative.summary`, `narrative.meaning` pass; `narrative.subject / trigger`, `narrative.arc`, `emotion.secondary`, `emotion.kind`, `emotion.arousal`, `emotion.appraisal.urgency / control`, `context.event / place / people / relationship_model / life_stage`, `salience.retrieval_cues / themes / recurrence / resilience / trajectory` are cut under the frozen rule; the `value` member of `valence`, `arousal`, `urgency` and `control` was never populated by any extractor. Task (a) passes pooled and in the synthetic and Pepys arms, fails in the conversational arm. Null precision: `bodily_sensation` is clean; `meaning` is inferred on 62–94 % of texts that state none. Full tables, per-arm results and deviations: `experiments/2026-10-17/RESULTS.md`.

## 8. Theoretical neutrality (summary of `theoretical-conflicts.md`)

Eleven conflicts were identified (basic vs constructed emotion, discrete vs dimensional, appraisal vs affect-program, emotion/mood/feeling, event vs person level, literary vs empirical narrative, memory taxonomies, gradient vs list, coping vs regulation, LLM functional concepts, collective vs individual memory). The single mechanism that keeps EDM neutral in all of them is `text + codings` with an explicit `relation` per coding and the rule that codes never replace the subject's words. This is already EDM's "interpretation only" constraint, made machine-readable.

## 9. Unverified claims register

Updated 2026-10-17 after the verification pass (`sources/verification_2026-10-17.json`; applied by `scripts/apply_verification.py`). Everything still tagged [KNOWLEDGE] in the deliverables is one of:

- **Whole frameworks reconstructed from knowledge**: none remaining. OCC (22 types, six groups, three branches), Gross (five families, antecedent/response, ERQ, extended-model stages), Elliot (approach/avoidance, trichotomous, 2×2, temperaments), Mayer–Salovey (four branches, 1990 components, MSCEIT) and Bronfenbrenner (five systems, PPCT) were each verified list-by-list and raised to FETCHED_SECONDARY. Wording drift recorded in `verified_against.corrections`: OCC writes "sorry for" where the list has "pity"; the Mayer–Salovey branch-3 heading is "Understanding and Analyzing Emotions"; Salovey & Mayer 1990's third heading is "Utilizing emotional intelligence"; the trichotomous framework is attributed by Elliot & Thrash to Elliot & Harackiewicz 1996.
- **Value lists still unverified or only partly verified (7 constructs; the 32 remaining K flags)**: Barrett emotional granularity (no value list to check); Singer & Blagov *specificity* (PARTIAL: the manual's non-specific subtypes are "episodic" and "generic", not "generic or extended"), *content* (PARTIAL: six categories confirmed, "achievement" not "achievement/mastery", "not classifiable" not found), *affect* (CONTRADICTED: the manual codes no affect; the positive/negative/mixed/neutral scheme is Lavallee et al. 2019, not Singer/Blagov); Pillemer *five features* (PARTIAL: three confirmed by an open book review, "believed accurate" only via Wikipedia); McAdams *coded constructs* (PARTIAL: five of seven confirmed; the two Pals 2006 labels not confirmed as Table 1 rows); McAdams *nuclear episodes* (CONTRADICTED on attribution: the list is the 1995 Life Story Interview verbatim, not the 2007/2008 revision, whose eight key scenes differ). All seven keep `value_source: KNOWLEDGE` with the source's version recorded.
- **Verified lists with caveats worth knowing**: Plutchik's three dyad lists were verified against Wikipedia (citing Plutchik 1991, Turner 2000, TenHouten 2016) because no open text copy of the 2001 figures exists; sources give awe/alarm and disapproval/disappointment as alternates. Ekman 1999's 15 items rest on a third-party ontology (SPICE/SON) quoting pp. 55–56. PAD: Mehrabian 1996 names the trait axis "Arousability"; "arousal-nonarousal" is the 1980 state scale. Russell: Study 3 used "drowsy" for "droopy". GEW: Scherer 2005 describes a 16-family prototype; 20 families is v2/v3 (verified in the v3.0 docx). Damasio's social-emotion examples in the verified source are contempt, pride, shame, embarrassment, admiration. McAdams agency themes: the 1996 manual has "power/impact" where 2001 has "empowerment". Goleman: the cited page lists the 12 competencies flat; the competency-to-domain grouping is still knowledge (partly corroborated by a University of Minnesota teaching page). Ainsworth: the originally cited Fraley page contains none of the subgroup or D material; the verifying sources were added to `fetched_urls`. Bartholomew & Horowitz's 1991 abstract defines the four patterns only by self/other valence; the labels come from secondary sources.
- **Literature cited outside the reference set** (never fetched): Mark & Pearson 2001; Fuchs 2013; Minkowski; Halbwachs 1925; Connerton 1989; Pargament 1997/2000; Davidson 1998; Gottman et al. 1996; Mitmansgruber et al. 2009; Keltner & Haidt 2003; Sedikides & Wildschut; Leary 1957; Erikson; Bonanno; Thorne & McLean; Bluck 2003; Hermans, Kempen & van Loon 1992 and Hermans 2001 (cited in `v0.9-proposal.md` §3); Lavallee et al. 2019; Kalawski 2010 (cited in `mfoem-term-requests.md`); HL7 FHIR Coding; W3C SKOS.
- **Known source problems**: Cowen & Keltner 2017 is internally inconsistent about pride vs relief in the 27; Hume's current docs no longer publish the 48/53 per-modality lists in the form the literature cites; EmotionML `occ-appraisals` shows `realization` in the HTML Note but not in the automated XML read; HUMAINE EARL is from an archive snapshot; SNOMED codes were verified on tx.fhir.org, not on the SNOMED browser; the Foley Center instrument URLs (sesp.northwestern.edu/foley/instruments/*) now 404 and the LSI-II lives on sites.northwestern.edu; Steunebrink, Dastani & Meyer 2009 has no findable open copy.

## 10. Recommended next steps

1. Decide the five domain renames and the 15 cuts/merges first; they are independent of any coding system.
2. File new-term requests with the MFOEM maintainers for awe, gratitude, relief, longing/nostalgia, tenderness, frustration; EDM's emotion list is the only place these seven are uncoded.
3. Run the ontology experiment on ranks 1–5 of §7 before deciding whether EDM-specific fields survive v0.9.
4. Publish the EDM vocabularies (`arc`, `tether`, `relationship`, `memory_type`, `temporal_profile`, `need`, `coping`) as SKOS with the crosswalk relations from `crosswalk.csv` as `skos:*Match` triples.
