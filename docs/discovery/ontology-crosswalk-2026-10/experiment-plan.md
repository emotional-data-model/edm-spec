# v0.9 field experiment plan (pre-registration draft)

Discovery output, 2026-10-17, branch `discovery/ontology-crosswalk`. Nothing has been run. This document fixes the corpus, the models, the measures and the pass thresholds **before** any extraction call is made, so that the v0.9 keep / redefine / cut decision per field is not fitted to the results. Changes to this document after the first run must be logged in §10.

Scope: the 47 affective fields of `v0.9-proposal.md` plus the two opt-in `trait` fields, extracted with the draft schema in `draft-schema/`. Two downstream tasks test whether the fields are *useful*, not only *repeatable*: (a) salience-weighted vs recency-weighted retention; (b) whether a stated `self_position` changes how raters read the rest of the record (REPORT.md §7 rank 12).

## 1. Questions

| # | Question | Decides |
|---|---|---|
| Q1 | Per field: does the same model give the same answer for the same text (repeatability)? | whether the field is extractable at all |
| Q2 | Per field: do different models agree (cross-model agreement)? | whether the field's definition is model-independent |
| Q3 | Per stated-only field: is it null when the text does not state it (null precision)? | whether the field respects interpretation-only |
| Q4 | Task (a): does ranking by salience fields surface what a later "what mattered this month" summary names, better than recency? | whether `salience.*` and `emotion.intensity` earn their place |
| Q5 | Task (b): does a stated `self_position` change rater interpretation of `arc`, `trajectory`, `need`, `valence_shift`? | whether `self_position` carries information the rest of the record does not |

## 2. Corpus: 50 synthetic texts

Written, not collected. No real person: no names, handles, diagnoses, workplaces, places or dates that identify anyone (the rule used for `synthetic-examples/`). English, 150–400 words, first person except the therapy-note and companion-transcript genres. Authored by the team, or drafted by a model that is **not** one of the four under test and then hand-edited; the author records a ground-truth sheet per text (§2.3) before extraction.

### 2.1 Event categories (Singer & Blagov content classification; labels knowledge-reconstructed, REPORT.md §9)

| Category | Texts | Notes |
|---|---|---|
| relationships | 12 | family, partner, friend, mentor, community |
| achievement / mastery | 10 | milestones, exams, performances, work |
| recreation / exploration | 8 | travel, hobbies, nature |
| guilt / shame | 8 | apologies, failures, secrets |
| life-threatening events | 6 | accidents, illness scares, emergencies (no diagnoses named) |
| drug / alcohol / tobacco use | 3 | quitting, relapse, a party |
| not classifiable | 3 | mundane or ambiguous entries |
| **Total** | **50** | |

### 2.2 Genre, valence and stated-content balance (crossed with 2.1)

| Dimension | Levels (count) |
|---|---|
| Genre | journal entry (20), companion-chat transcript (15), therapy session note (10), short memoir / wiki paragraph (5) |
| Valence as authored | positive (18), negative (18), mixed (14) |
| Stated insight (`narrative.meaning`) present | yes (25) / no (25) |
| Stated self-position (`narrative.self_position`) present | yes (20) / no (30) |
| Stated bodily sensation | yes (20) / no (30) |
| Stated causal attribution | yes (20) / no (30) |
| Stated memory function (why it matters) | yes (20) / no (30) |
| Explicit turning-point claim | yes (12) / no (38) |
| Trait self-description (attachment / regulation language) | yes (8) / no (42) |

The "no" texts for each stated-only field are the null-precision set for Q3. A text may be "yes" on several dimensions.

### 2.3 Ground-truth sheet (per text, authored before extraction)

`event_category`, genre, authored valence, the presence flags above, and for each "yes" flag the span of text that states it. Plus the month assignment and salience intent for task (a) (§5.1). The sheet is committed with the corpus and never shown to a model.

## 3. Models and runs

| Slot | Model (to be fixed at pre-registration with exact ID and date) | Provider |
|---|---|---|
| M1 | Claude, current Sonnet-class model | anthropic |
| M2 | GPT, current general model | openai |
| M3 | Gemini, current Pro-class model | google |
| M4 | one open-weight model served by a hosted API or locally (e.g. a 70B-class instruction model) | open_weight |

- 5 repeats per text per model, provider-default sampling (temperature 1 where settable), fresh context per call, same prompt. Repeatability at default sampling is the deployment-relevant quantity; a temperature-0 run is not pre-registered.
- One prompt for all models: the field definitions from `draft-schema/fragments/*.json` (`description` + `x_constraints`), the interpretation-only rule ("populate only what the text states; otherwise null"), and the output shape `text` / `value` only. **EDM codes are applied afterwards by the deterministic coder in `scripts/v09_layout.py`**, so coding is not a source of variance and output tokens stay small.
- Calls: 50 × 4 × 5 = **1,000 extraction calls**. Pilot first: 5 texts × 4 models × 2 repeats (40 calls) to catch prompt and parsing failures; pilot results are discarded.
- Every output is validated against `draft-schema/edm.v0.9.full.schema.json`; an invalid output counts as a failed repeat (recorded, not re-sampled).
- Each run records `telemetry.extraction_model`, `extraction_provider` and `field_confidence` (the model is asked for per-field confidence; it is analysed, not used for scoring).

## 4. Measures and pre-registered thresholds

### 4.1 Field shapes and their measures

| Shape | Fields | Repeatability (within model, 5 repeats) | Cross-model agreement (per-model modal / medoid answer) |
|---|---|---|---|
| **T** short text | subject, trigger, harm, drive, integration, meaning, identity_link, valence_shift, self_position, meta, bodily_sensation, event, place, tether.referent, tether.stake | mean pairwise cosine of sentence embeddings ≥ 0.70 on ≥ 80 % of populated texts | mean pairwise cosine of per-model medoids ≥ 0.60 |
| **S** long text | summary | ROUGE-L F ≥ 0.50 between repeats | ROUGE-L F ≥ 0.40 between model medoids |
| **C** coded single | primary, kind, temporal_profile, appraisal.attribution, event_category, relationship, relationship_model, life_stage, scope.text, scope.direction, memory_type, tether.type, recurrence, persistence.text, persistence.decay, trajectory, action_tendency, need, temporal_focus, risk_posture, coping, trait.attachment_style, trait.regulation_state | modal agreement ≥ 0.80 (≥ 4 of 5 repeats) on ≥ 80 % of texts | Krippendorff's α (nominal) ≥ 0.67 over modal labels |
| **L** list / coded list | secondary, arc, people, retrieval_cues, themes, function, resilience | mean pairwise Jaccard ≥ 0.60 (text normalised, embedding-matched at cosine ≥ 0.8) | mean pairwise Jaccard ≥ 0.40 |
| **D** dimension | valence, arousal, intensity, appraisal.urgency, appraisal.control | `value`: SD ≤ 0.10; `text`: weighted κ ≥ 0.60 | ICC(2,1) ≥ 0.60 on `value`; weighted κ ≥ 0.60 on `text` |
| **N** number | linkage_strength | SD ≤ 0.10 | ICC(2,1) ≥ 0.60 |
| **B** boolean | turning_point | agreement ≥ 0.90 | α ≥ 0.67 |

Embeddings: one fixed open-weight sentence-embedding model, named at pre-registration; the same model for every comparison. α computed with the standard nominal distance; ICC on the 50 × 4 matrix of per-model means.

### 4.2 Null precision (Q3), stated-only fields

For `meaning`, `self_position`, `bodily_sensation`, `turning_point`, `kind`, `arousal`, `appraisal.attribution`, `function`, `trait.attachment_style`, `trait.regulation_state`:

- on the "no" texts (§2.2), null rate ≥ 0.95 per model (a populated value on a text that does not state it is an inference, which the spec forbids);
- on the "yes" texts, non-null rate ≥ 0.80 per model, and the extracted text must overlap the ground-truth span (embedding cosine ≥ 0.70) in ≥ 0.80 of those cases.

### 4.3 Per-field decision rule (fixed now)

A field **passes** when it meets its repeatability threshold on ≥ 3 of 4 models, its cross-model threshold, and (if stated-only) both null-precision thresholds.

| Outcome | Reading | Action proposed for v0.9 |
|---|---|---|
| passes everything | extractable and model-independent | keep as drafted |
| repeatable in ≥ 3 models but cross-model α < 0.67 | definition is model-dependent | redefine (tighten `description` / `x_constraints`), re-run that field only |
| repeatable in ≤ 2 models | not reliably extractable | cut from the canonical profiles or move to `extensions`; keep text in migration |
| null precision < 0.95 | invites inference | redefine with explicit null rule; if still failing, cut |
| `D` value fails but text passes | number is noise | drop `value` from the field (keep ordinal) |

Thresholds are the conventional reliability bounds (α 0.67 tentative / 0.80 firm; ICC 0.60 "good"), chosen before seeing any output. A field that lands within 0.05 of a threshold is reported as borderline, not rounded up.

### 4.4 Per-field threshold table

Shape codes from §4.1; "stated-only" marks the Q3 set. Thresholds are those of the shape unless noted.

| Field | Shape | Stated-only | Extra |
|---|---|---|---|
| narrative.subject | T | | |
| narrative.trigger | T | | |
| narrative.harm | T | | null allowed when no harm is stated; null-rate not scored |
| narrative.drive | T | | |
| narrative.integration | T | | |
| narrative.summary | S | | faithfulness spot-check: 20 summaries × 2 human readers, no unsupported sentence |
| narrative.meaning | T | yes | |
| narrative.identity_link | T | | |
| narrative.turning_point | B | yes | |
| narrative.arc | L | | modal first element must also meet C thresholds |
| narrative.valence_shift | T | | |
| narrative.self_position | T | yes | task (b) |
| emotion.primary | C | | α ≥ 0.80 required (firm bound; this is the headline field) |
| emotion.secondary | L | | |
| emotion.kind | C | yes | |
| emotion.valence | D | | text α ≥ 0.80 required |
| emotion.arousal | D | yes | |
| emotion.intensity | D | | value only (text optional); task (a) input |
| emotion.meta | T | | |
| emotion.bodily_sensation | T | yes | |
| emotion.temporal_profile | C | | EDM-specific values (spiraling, dragging, suspended) reported separately |
| emotion.appraisal.urgency | D | | |
| emotion.appraisal.control | D | | |
| emotion.appraisal.attribution | C | yes | |
| context.event | T | | |
| context.event_category | C | | also scored against the author's category: accuracy ≥ 0.80 |
| context.place | T | | |
| context.people | L | | |
| context.relationship | C | | deprecated values counted as their replacement |
| context.relationship_model | C | | |
| context.life_stage | C | | |
| context.scope (text, direction) | C | | scored as two C fields |
| salience.memory_type | C | | |
| salience.tether (type) | C | | referent and stake scored as T |
| salience.retrieval_cues | L | | |
| salience.themes | L | | |
| salience.recurrence | C | | |
| salience.persistence (text, decay) | C | | scored as two C fields |
| salience.linkage_strength | N | | task (a) input |
| salience.function | L | yes | |
| salience.resilience | L | | |
| salience.trajectory | C | | |
| motivation.action_tendency | C | | |
| motivation.need | C | | |
| motivation.temporal_focus | C | | |
| motivation.risk_posture | C | | |
| motivation.coping | C | | |
| trait.attachment_style | C | yes | expected to fail null precision; that result is the point |
| trait.regulation_state | C | yes | as above |

## 5. Task (a): salience-weighted vs recency-weighted retention

### 5.1 Setup

- The 50 texts are assigned to **5 synthetic months × 10 entries**, each with a day number, at authoring time. For each month the author writes, before extraction, a short "what mattered this month" summary that names 3–5 entries by content (the held-out target), and records which entries they intend to be the salient ones.
- Retention policies, each keeping **k = 3** of 10 entries per month:
  - **recency**: the 3 latest entries;
  - **salience**: the 3 highest on the pre-registered score `S = mean(emotion.intensity.value, salience.linkage_strength, persistence_rank)` where `persistence_rank` maps the EDM persistence code transient / short / enduring / chronic to 0.25 / 0.5 / 0.75 / 1.0 and missing components are dropped from the mean;
  - **random**: expectation over 1,000 draws (no model calls), as the floor.
- Per model under test, the salience policy uses that model's modal extraction (over its 5 repeats), so the task is also run four times.

### 5.2 Measure

Hit rate = fraction of entries named in the month summary that are among the retained 3, averaged over the 5 months. Whether a retained entry is "named" is decided by matching the summary's items to entries using the ground-truth mapping made at authoring time (no model judgement needed). Random floor for 3 of 10 with 3–5 named items is about 0.30.

### 5.3 Pass thresholds (pre-registered)

- salience hit rate − recency hit rate ≥ **0.15** absolute, averaged over months, for ≥ 3 of 4 models; and
- salience hit rate ≥ random floor + 0.20.

If salience beats recency only when a single component of `S` is used, that component is reported and the others are flagged as not contributing. A result where recency wins is a finding against the salience domain as a retention signal, not against the fields' repeatability.

## 6. Task (b): does stated `self_position` change interpretation?

### 6.1 Setup

- Items: the 20 texts with a stated self-position; for each, the modal M1 extraction with `self_position` **removed** is the base artifact.
- Conditions, shown to raters as the artifact's JSON with the four target fields blanked:
  - **A** base artifact (no `self_position`);
  - **B** base artifact + `self_position` as extracted;
  - **B′ (control)** base artifact + one non-informative field restored (`context.place`), to separate "any extra field" from "this field".
- Raters: the four models, 3 repeats each, plus two human raters if available, each rating all 20 × 3 items in randomised order, blind to condition. The rater fills `narrative.arc` (first element), `salience.trajectory`, `motivation.need` and `narrative.valence_shift` from the artifact alone (the source text is not shown).

### 6.2 Measures and thresholds

- Change rate per field = fraction of items where the modal rating under B differs from the modal rating under A; the same for B′ vs A.
- `self_position` **carries information** when change rate(B vs A) − change rate(B′ vs A) ≥ **0.20** on at least two of the four target fields, for ≥ 3 of 4 model raters (and for the human raters if present).
- Secondary, descriptive: which direction ratings move (e.g. `need` toward `belonging` when the self-position is relational), and how often `self_position` was stated at all per genre (expected: rare in journal entries, common in therapy notes).

A null result means the field is still a legitimate stated-only record of what the subject said, but the claim that it changes downstream interpretation is dropped from the proposal.

## 7. Analysis plan

1. Parse and validate every output; log invalid repeats.
2. Apply the deterministic coder; compute §4 measures per field per model with the scripts committed alongside this plan before the run (`scripts/experiment/` to be added; seeds fixed).
3. Fill §4.4 with pass / borderline / fail and the decision from §4.3.
4. Run §5 and §6 on the modal extractions.
5. Report in `experiment-results.md` with every number, including failed thresholds; no field is re-run except under the §4.3 "redefine" branch, and such re-runs are reported as second runs.

## 8. Cost estimate

Token assumptions (measured in the pilot and corrected there): prompt with field definitions and rules ≈ 6,000 tokens, text ≈ 400, output (text / value only, no codings) ≈ 1,200.

| Call set | Calls | Input tokens | Output tokens |
|---|---|---|---|
| Extraction, 4 models | 1,000 | 6.4 M | 1.2 M |
| Pilot | 40 | 0.26 M | 0.05 M |
| Task (b) raters, 4 models × 20 × 3 conditions × 3 repeats | 720 | 1.8 M (≈ 2,500 each) | 0.15 M (≈ 200 each) |
| Task (a) | 0 | matching is by ground truth | |
| Embeddings (≈ 25 text fields × 1,000 artifacts) | 25,000 short strings | ≈ 0.5 M | |

List prices assumed on 2026-10-17 (USD per million tokens, input / output; **verify against the providers' price pages on the run date**): Claude Sonnet-class 3 / 15; GPT general model 1.25 / 10; Gemini Pro-class 1.25 / 10; hosted open-weight 0.15 / 0.60; embeddings 0.02.

| Model | Extraction + pilot | Task (b) raters | Subtotal |
|---|---|---|---|
| M1 Claude | 1.66 M × 3 + 0.31 M × 15 ≈ 4.98 + 4.69 | 0.45 M × 3 + 0.04 M × 15 ≈ 1.35 + 0.56 | ≈ 11.6 |
| M2 GPT | 1.66 M × 1.25 + 0.31 M × 10 ≈ 2.08 + 3.13 | 0.56 + 0.38 | ≈ 6.2 |
| M3 Gemini | same as M2 | same | ≈ 6.2 |
| M4 open-weight | 0.25 + 0.19 | 0.07 + 0.02 | ≈ 0.5 |
| Embeddings | | | ≈ 0.1 |
| **Total** | | | **≈ USD 25**, upper bound ≈ USD 60 with retries, one redefine re-run of up to 10 fields, and prompt growth |

Prompt caching (Claude, OpenAI) would cut the input share by most of its cost; it is not assumed. Human rater time for §6 (2 raters × 60 items) and the §4.4 summary spot-check (2 readers × 20) is the larger real cost and is outside this estimate.

## 9. What this plan does not test

- Non-English text, audio or image sources (`meta.source_type` other than text).
- Longitudinal aggregation of `trait.*` across artifacts (deliberately; the spec forbids it).
- Human–model agreement on the 47 fields beyond the two spot-checks; a human-coded gold set is a separate study.
- The Anthropic 171 audit hook (`v0.9-proposal.md` §5); it could be logged in `telemetry.extraction_notes` for M1 at no extra cost, descriptively.

## 10. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-10-17 | Plan written; no run yet | |
