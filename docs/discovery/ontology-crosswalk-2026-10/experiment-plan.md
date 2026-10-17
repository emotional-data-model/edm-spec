# v0.9 field experiment plan (PRE-REGISTRATION, frozen 2026-10-17)

Discovery output, branch `discovery/ontology-crosswalk`. This document fixes the corpus, the models, the prompts, the measures and the pass thresholds **before** any extraction call is made, so that the v0.9 keep / redefine / cut decision per field is not fitted to the results. The commit that carries this version is titled `pre-registration frozen`; no extraction call is issued before that commit exists. Changes after the first run are logged in §10 and reported as deviations in `experiments/2026-10-17/RESULTS.md`.

Scope: the 47 affective fields of `v0.9-proposal.md`, Full profile of the draft schema in `draft-schema/` (after the 2026-10-17 rulings: Essential = 12 fields, `extensions` allowed in every composite, `text` of coded fields validated as a recommended vocabulary, codings still validated). The two opt-in `trait` fields are **not** extracted in this run (they belong to no canonical profile). Two downstream tasks test whether the fields are *useful*, not only *repeatable*: (a) salience-weighted vs recency-weighted retention; (b) whether a stated `self_position` changes how raters read the rest of the record.

Run directory: `experiments/2026-10-17/` (corpus manifest, prompts, pinned models and prices, raw checkpoints, spend, scoring, RESULTS.md, STATUS.md).

## 1. Questions

| # | Question | Decides |
|---|---|---|
| Q1 | Per field: does the same model give the same answer for the same text (repeatability)? | whether the field is extractable at all |
| Q2 | Per field: do different models agree (cross-model agreement)? | whether the field's definition is model-independent |
| Q3 | Per stated-only field: is it null when the text does not state it (null precision; synthetic arm only, where ground truth exists)? | whether the field respects interpretation-only |
| Q4 | Task (a): does ranking by salience fields surface what a later summary / back-reference / benchmark question names, better than recency? | whether `salience.*` and `emotion.intensity` earn their place |
| Q5 | Task (b): does a stated `self_position` change rater interpretation of `arc`, `trajectory`, `need` (and, descriptively, `valence_shift`)? | whether `self_position` carries information the rest of the record does not |

## 2. Corpus: three arms of 50 texts (150)

Built by `experiments/2026-10-17/scripts/build_corpus.py` (seed 20261017) into `experiments/2026-10-17/corpus/corpus_manifest.jsonl` (one record per text: id, arm, block, order, locator, sha256 of the exact text sent, word count; text included for the synthetic and Pepys arms) and `corpus/task_a_blocks.json` (retention blocks, named items and their evidence). Every text is sent to the extractors exactly as hashed.

### 2.1 Synthetic arm (50; ids S01–S50)

Written for this experiment, not collected. No real person: no names, handles, diagnoses, workplaces, identifiable places or calendar dates. English, 150–400 words. Authored by a model that is **not** one of the four extractors nor the judge (Claude Fable 5.1, the session model), against a seeded design matrix (`corpus/synthetic_design_matrix.{json,csv}`) that fixes every quota below by construction, then checked programmatically (every TRUE flag has a span that is an exact substring of the text; every FALSE flag has none). Files: `corpus/synthetic_texts_months_1-3.json`, `corpus/synthetic_texts_months_4-5.json`.

| Dimension | Levels (count) |
|---|---|
| Event category (Singer & Blagov content classification) | relationships 12, achievement / mastery 10, recreation / exploration 8, guilt / shame 8, life-threatening events 6, drug / alcohol / tobacco use 3, not classifiable 3 |
| Genre | journal entry 20, companion-chat transcript 15, therapy session note 10, memoir / wiki paragraph 5 (first person except the therapy note and the transcript) |
| Valence as authored | positive 18, negative 18, mixed 14 |
| Stated insight (`narrative.meaning`) | yes 25 / no 25 |
| Stated self-position (`narrative.self_position`) | yes 20 / no 30 |
| Stated bodily sensation (`emotion.bodily_sensation`) | yes 20 / no 30 |
| Stated causal attribution (`emotion.appraisal.attribution`) | yes 20 / no 30 |
| Stated memory function (`salience.function`) | yes 20 / no 30 |
| Explicit turning-point claim (`narrative.turning_point`) | yes 12 / no 38 |
| Trait self-description (attachment / regulation language) | yes 8 / no 42 (trait fields are not extracted; this flag tests whether extractors leak trait language into other fields, reported descriptively) |
| Month × day (task a) | 5 synthetic months × 10 entries; 4 entries per month authored as salient (20) and named in the author's month summary; the other 6 authored as routine |

Ground-truth sheet = the design matrix row plus the quoted spans and the month summaries. It is committed with the corpus and never shown to a model.

### 2.2 Conversational arm (50; third-party benchmarks, referenced by path)

| Source | Licence (read 2026-10-17) | Handling | Texts |
|---|---|---|---|
| LoCoMo (`../deepadata-com-retrieval/eval_data/Episodic/LoCoMo/locomo10.json`, snap-research/locomo) | CC BY-NC 4.0 (upstream `LICENSE.txt`): redistribution for non-commercial purposes only | edm-spec is MIT, so the text is **not copied** into this repository: the manifest records path, `sample_id`, `session_n`, date and sha256; the runner resolves the text from the retrieval repo at run time (`corpus/.resolved_texts.jsonl`, gitignored) | 2 conversations × sessions 1–10 = **20** (`conv-42`, `conv-48`: the two 10+-session conversations with the fewest words). Rendering: one line per turn, `Speaker: text`, image captions appended as `[shares image: …]` |
| LongMemEval-S (`../deepadata-com-retrieval/tests/longmemeval/data/longmemeval_s.json`, xiaowu0162/LongMemEval) | MIT (GitHub repository licence) | referenced by path and sha256 like LoCoMo, for symmetry; copying would be permitted | 3 `multi-session` questions × 10 sessions = **30** (`9aaed6a3`, `09ba9854`, `3fdac837`: 2 answer sessions each, user turns 80–600 words, smallest total; 8 seeded distractor sessions from the same haystack, same size filter). Rendering: the session's **user turns only**, `User: ` prefix, chronological haystack order |

No figure from the retrieval repository's own Phase 3 or N11 reports is reproduced here or in the results.

### 2.3 Pepys arm (50; public domain)

`../deepadata-com-retrieval/tests/pepys/corpus/scenes.json` (Diary of Samuel Pepys, 1665, Project Gutenberg #4200; 310 day-entries). Five months × 10 entries, entries 150–700 words, seeded sample, kept in date order: months **1, 4, 6, 9, 12** (ids `P1665-MM-DD`). Text is committed (public domain).

Back-references for task (a) are taken from the diary itself: an entry is *referred back to* when a later entry within about 90 days shares ≥ 3 distinctive terms with it (document frequency ≤ 5 % of the 310 entries, ≥ 4 letters, not a stopword). The 4 most-referenced entries of each month are the named items; the referencing dates and shared terms are recorded in `task_a_blocks.json`. This is a lexical operationalisation of "later entries' own back-references", fixed before extraction; it is not hand-coded.

## 3. Models, sampling, prompts (pinned)

Pinned from each provider's live `/models` listing and public price page on 2026-10-17 (`experiments/2026-10-17/models.json`, raw listings in `_model_lists_raw.json`). Prices are USD per million tokens, input / cached input / output.

| Slot | Model ID | Provider | Price in / cached / out | Note |
|---|---|---|---|---|
| M1 | `claude-sonnet-5-5` | anthropic | 2.00 / 0.20 / 10.00 (cache write 2.50) | Claude Sonnet 5.5 |
| M2 | `claude-haiku-5-5` | anthropic | 0.10 / 0.01 / 0.50 (cache write 0.125) | Claude Haiku 5.5 |
| M3 | `gpt-6.1-sol` | openai | 2.00 / 0.10 / 10.00 | newest OpenAI general model on 2026-10-17. `gpt-6-astra` (10.00 / 1.00 / 50.00) is the premium tier and alone would exceed the USD 80 budget; excluded, founder may re-pin |
| M4 | `kimi-k2.6` | kimi (Moonshot, `https://api.moonshot.ai/v1`) | 0.95 / 0.16 / 4.00 | Kimi K2 latest; `kimi-k3` (3.00 / 0.30 / 15.00) exists and was not chosen |
| Judge | `claude-opus-5-5` | anthropic | 4.00 / 0.20 / 20.00 (cache write 5.00) | equivalence judge for free-text fields; **never used for extraction or as a task (b) rater** |

- **Sampling:** provider defaults for every extractor: no `temperature`, `top_p`, `effort` or thinking configuration is sent (Claude Sonnet 5.5 and Haiku 5.5 reject non-default sampling; adaptive thinking is their default). Fresh context per call. Repeatability at default settings is the deployment-relevant quantity.
- **Runs:** 150 texts × 4 extractors × 5 repeats = **3,000 extraction calls** at the Full profile of the draft v0.9 layout, one shared extraction prompt (Appendix A; `experiments/2026-10-17/prompts/extraction_system.txt`, generated from `draft-schema/fragments/*.json` by `scripts/prompts.py`). Output is `text` / `value` only; EDM codings are applied afterwards by the deterministic coder (`scripts/v09_layout.py`), so coding is not a source of variance.
- **Pilot:** 3 texts (one per arm) × 4 extractors × 1 repeat = 12 calls to measure tokens and catch parsing failures; pilot outputs live in `raw/pilot/` and are excluded from scoring.
- **Checkpointing:** every call is appended to `experiments/2026-10-17/raw/<model>/<arm>.jsonl` (request hash, usage, cost at list price, raw text, parsed object, parse / transport error) before the next call on that file; a run resumes by skipping (text, repeat) pairs already present. No completed call is ever repeated.
- **Failed repeats:** an output that is not a JSON object is a failed repeat (recorded, not re-sampled). Transport errors (rate limits, 5xx) are retried with back-off; they do not produce outputs and are not repeats.
- **Prompt caching:** Anthropic 1-hour cache on the system prompt; OpenAI automatic prefix caching. Caching changes cost, not outputs.
- **Budget:** USD 80 total (extraction + judge + raters). Projection = spent + remaining calls × mean cost so far, plus the judge and rater reserves (§8), checked before the run and after every 500 calls; if it exceeds USD 80 the run stops and `STATUS.md` says why.
- **Pre-registered budget fallback (decided now, before any call):** if the **pilot** projects a total above USD 80 with provider defaults, the two Claude extractors are run with `output_config.effort = "low"` (the only cost lever that does not alter sampling) and this is logged in §10 as deviation D1 before the main run starts. If the projection still exceeds USD 80, the run does not start.

## 4. Measures and frozen thresholds

### 4.1 Thresholds (ruling 2026-10-17, verbatim)

> coded fields: repeatability Fleiss κ≥0.70, cross-model κ≥0.40 (≥0.70 repeat but <0.40 cross = "interpretive, not comparable"); free-text fields: judge-equivalence ≥0.80 repeatability, ≥0.60 cross-model, judge model never used for extraction; dimensions: ICC≥0.75 / ≥0.50; any field failing repeatability is cut or moved to extensions; task (a) pass = salience-weighted retention beats recency-weighted by ≥10 points on recall of items named in the later summary; task (b) pass = ≥20% of rater readings of arc/trajectory/need shift with self_position present and control-field shift <10%.

These supersede the draft thresholds of the 2026-10-17 morning version of this document (α / cosine / Jaccard / SD bounds), which were never run against.

### 4.2 Field shapes and how each is scored

| Shape | Fields (47) | Repeatability (within model, 5 repeats) | Cross-model agreement (4 models) |
|---|---|---|---|
| **C** coded single | emotion.primary, emotion.kind, emotion.temporal_profile, emotion.appraisal.attribution, context.event_category, context.relationship, context.relationship_model, context.life_stage, context.scope.text, context.scope.direction, salience.memory_type, salience.tether.type, salience.recurrence, salience.persistence.text, salience.persistence.decay, salience.trajectory, motivation.action_tendency, motivation.need, motivation.temporal_focus, motivation.risk_posture, motivation.coping; plus the `text` of the five dimensions (emotion.valence, emotion.arousal, emotion.intensity, emotion.appraisal.urgency, emotion.appraisal.control) | **Fleiss κ** over subjects = texts, raters = the 5 repeats, categories = normalised labels (lower-cased, trimmed, deprecated values mapped to their replacement per `v09_layout.DEPRECATED_VALUES`, null = its own category "null"). Pass ≥ 0.70 | **Fleiss κ** over subjects = texts, raters = the 4 models, each model represented by its modal label across its repeats (ties → the label of the earliest repeat). Pass ≥ 0.40 |
| **CL** coded list | narrative.arc, emotion.secondary, salience.function | scored as C on the **first listed element** (normalised; empty list = "null"); mean pairwise Jaccard of the normalised sets reported descriptively | as C on the per-model modal first element |
| **T** free text | narrative.subject, trigger, harm, drive, integration, meaning, identity_link, valence_shift, self_position; emotion.meta, bodily_sensation; context.event, place; salience.tether.referent, tether.stake | **Judge equivalence**: for each text × field the judge (Opus 5.5) receives all answers from all models and repeats (≤ 20, indexed) and groups them into equivalence classes; null answers form the "null" class. Repeatability per model = mean over texts of the fraction of that model's repeat pairs that fall in the same class. Pass ≥ 0.80 | Cross-model = mean over texts of the fraction of model pairs whose **representatives** (the answer from each model's largest within-model class) fall in the same class. Pass ≥ 0.60 |
| **S** long text | narrative.summary | as T | as T |
| **L** free-text list | context.people, salience.retrieval_cues, salience.themes, salience.resilience | as T, the whole list (joined, sorted) presented to the judge as one answer | as T |
| **D** dimension value | emotion.valence.value, arousal.value, intensity.value, appraisal.urgency.value, appraisal.control.value | **ICC(2,1)** (two-way random, single measures) over texts × repeats, computed on texts where all 5 repeats give a number (coverage reported). Pass ≥ 0.75 | ICC(2,1) over texts × models on per-model means of the repeats. Pass ≥ 0.50 |
| **N** number | salience.linkage_strength | as D | as D |
| **B** boolean | narrative.turning_point | as C (categories true / false / null) | as C |

Judge calls batch all answers for one text × field into one call, and several fields of one text into the same call (five field groups: `narrative.summary` alone; the other 19 free-text fields in four groups of 4–5), so no answer is judged more than once and no pairwise calls are made. The judge sees the source text and runs at `output_config.effort = "low"` (a grouping task; fixed now, not a cost fallback). Judge prompt: Appendix A.

### 4.3 Decision rule per field (fixed now)

Applied per arm and pooled over all 150 texts; the pooled result drives the v0.9 proposal, the per-arm results are reported beside it.

| Outcome | Condition | Reading | Action for v0.9 |
|---|---|---|---|
| **pass** | repeatability threshold met on ≥ 3 of 4 models **and** cross-model threshold met | extractable and model-independent | keep as drafted |
| **interpretive, not comparable** | repeatability threshold met on ≥ 3 of 4 models **but** cross-model threshold not met | the definition is model-dependent | keep as text; mark the field "interpretive" in the schema description; no cross-system comparison claim; redefine `description` / `x_constraints` before any second run |
| **cut** | repeatability threshold not met on ≥ 2 of 4 models | not reliably extractable | cut from the canonical profiles or move to `extensions`; text preserved in migration |

A field whose statistic lands within 0.05 of a threshold is reported as **borderline** with the outcome the rule gives, never rounded up. A field that is null in ≥ 90 % of all outputs pooled is reported as **sparse**: its κ is still computed but the outcome is flagged, since agreement on null is not evidence the field is extractable.

### 4.4 Null precision (Q3; synthetic arm only)

For the stated-only fields with a ground-truth flag (`narrative.meaning`, `narrative.self_position`, `emotion.bodily_sensation`, `emotion.appraisal.attribution`, `salience.function`, `narrative.turning_point`): on the "no" texts, null rate per model (target ≥ 0.95; a populated value on a text that does not state it is an inference); on the "yes" texts, non-null rate per model (target ≥ 0.80). Descriptive: these targets are reported and discussed but are **not** part of the §4.3 outcome, which is fixed by the verbatim thresholds. `emotion.kind` and `emotion.arousal` have no ground-truth flag and are reported by null rate only.

### 4.5 Also reported, descriptively

Non-canonical rate per coded field (share of non-null answers outside the recommended vocabulary); `field_confidence` summaries; invalid-output rate per model; `context.event_category` accuracy against the authored category (synthetic arm); trait-language leakage (whether the 8 trait-language synthetic texts produce attachment / regulation words anywhere in the output).

## 5. Task (a): salience-weighted vs recency-weighted retention

### 5.1 Setup (all arms)

Blocks of 10 ordered entries; each retention policy keeps **k = 3** per block.

- **recency**: the 3 latest entries by block order (synthetic day; LoCoMo session number; LongMemEval haystack date order; Pepys date).
- **salience**: the 3 highest on `S = mean(emotion.intensity.value, salience.linkage_strength, persistence_rank)` where `persistence_rank` maps the EDM persistence code (from the modal `salience.persistence.text` / `.decay` via the fixed recode table in `v09_layout.py`) transient / short / enduring / chronic → 0.25 / 0.5 / 0.75 / 1.0; numeric components are the **median** over that model's repeats; missing components are dropped from the mean; an entry with no component is ranked last. Run once per extractor model (4 runs).
- **random**: expectation over 1,000 seeded draws (no model calls).

| Arm | Blocks | Named items ("what the later record names") | Hit rate per block |
|---|---|---|---|
| synthetic | 5 months | the 4 entries named in the author's month summary (ground-truth mapping, no model judgement) | named entries retained / 4 |
| conversational, LoCoMo | 2 conversations (sessions 1–10) | the benchmark's own QA items whose evidence lies in sessions 1–10 (87 and 92 probes); a probe is hit when every evidence session it needs is retained | hit probes / probes |
| conversational, LongMemEval | 3 questions | the benchmark's `answer_session_ids` (2 per question) | answer sessions retained / 2 |
| pepys | 5 months | the 4 most back-referenced entries (§2.3) | named entries retained / 4 |

### 5.2 Pass threshold (verbatim: beats recency by ≥ 10 points on recall of named items)

Per arm and pooled: mean over blocks of (salience hit rate − recency hit rate) **≥ 0.10** (10 points) for ≥ 3 of 4 extractor models. Also reported: each component of `S` alone (if only one component carries the effect, the others are flagged as not contributing); the random floor; LoCoMo results per QA category. A result where recency wins is a finding against the salience domain as a retention signal, not against the fields' repeatability.

## 6. Task (b): does stated `self_position` change interpretation?

### 6.1 Setup

- Items: the 20 synthetic texts with a stated self-position (ground truth). Base artifact = the **M1 (`claude-sonnet-5-5`) modal extraction** of the text with `narrative.self_position` removed and the four target fields (`narrative.arc`, `salience.trajectory`, `motivation.need`, `narrative.valence_shift`) blanked. If M1 returned null `self_position` for an item, the item uses the authored span instead and this is reported.
- Conditions (the source text is never shown): **A** base; **B** base + `self_position`; **B′ (control)** base + `context.place` restored instead.
- Raters: the four extractor models, 3 repeats each, every item × condition in seeded random order, fresh context per call: 20 × 3 × 4 × 3 = **720 calls**. Rater prompt: Appendix A. The judge model is not a rater.

### 6.2 Measures and pass threshold (verbatim: ≥ 20 % of rater readings of arc / trajectory / need shift with self_position present and control-field shift < 10 %)

- For each item × rater model, the **reference reading** of a field is that rater's modal reading under A. A rater reading under B (or B′) **shifts** when its normalised label differs from the reference. Shift rate = shifted readings / all readings, pooled over the three coded target fields (`arc` first element, `trajectory`, `need`) and reported per field as well.
- **Pass:** shift rate(B) ≥ 0.20 **and** shift rate(B′) < 0.10, pooled over the three fields and the four raters; also reported per rater and per field. `valence_shift` (free text) is reported descriptively by exact normalised match.
- Secondary, descriptive: direction of movement (e.g. `need` toward `belonging` when the self-position is relational); how often `self_position` was extracted at all per genre.

## 7. Analysis plan

1. Parse and validate every output (`experiments/2026-10-17/scripts/score.py`): JSON object with the 47 keys; shape coercion; invalid repeats logged.
2. Normalise labels; compute §4.2 statistics per field, per model, per arm and pooled; apply §4.3; produce the per-field table (pass / interpretive / cut, with borderline and sparse flags).
3. Judge calls for T / S / L fields (`scripts/judge.py`, checkpointed to `raw/judge/*.jsonl`).
4. Task (a) (`scripts/task_a.py`) on the modal / median extractions; task (b) (`scripts/task_b.py`, checkpointed to `raw/rater/*.jsonl`).
5. Write `experiments/2026-10-17/RESULTS.md`: per-field table per arm and pooled, task results, spend incurred, every deviation from this document and why. Update `REPORT.md` §7 with the outcome per ranked construct.

Fleiss κ: standard formula over the subjects × categories count matrix, with a varying number of raters per subject allowed (subjects with fewer than 2 valid raters dropped and counted). ICC(2,1): Shrout & Fleiss two-way random single measures. Implemented in `scripts/stats.py` with unit checks against textbook examples.

## 8. Cost (pre-run estimate at pinned list prices)

Token assumptions before the pilot: extraction system prompt ≈ 4,600 tokens (cached after the first call per provider where caching applies), source text ≈ 450 tokens, output ≈ 1,500 tokens; Claude extractors add thinking tokens of unknown size (measured in the pilot).

| Call set | Calls | Estimate (USD) |
|---|---|---|
| Extraction M1 Sonnet 5.5 | 750 | input 0.45 M × 2 + cached 3.4 M × 0.20 + output (1.1 M + thinking) × 10 ≈ 13–25 |
| Extraction M2 Haiku 5.5 | 750 | ≈ 1 |
| Extraction M3 gpt-6.1-sol | 750 | input 0.4 M × 2 + cached 3.4 M × 0.10 + output 1.1 M × 10 ≈ 12 (+ reasoning tokens if billed) |
| Extraction M4 kimi-k2.6 | 750 | ≈ 4–7 |
| Pilot | 12 | < 1 |
| Judge Opus 5.5 (150 texts × 5 field groups) | 750 | ≈ 4 k in + 0.6 k out each ≈ 12 + thinking ≈ **16 (reserve)** |
| Task (b) raters | 720 | ≈ 2 k in + 0.2 k out each ≈ **5 (reserve)** |
| **Total** | 2,982 + judge/raters | **≈ 50–70; hard stop at 80** |

The runner re-projects from measured usage (§3). Actual spend is reported in RESULTS.md from the per-call usage records.

## 9. What this plan does not test

- Non-English text, audio or image sources.
- The `trait` fields (not extracted; see §4.4 for trait-language leakage).
- Longitudinal aggregation across artifacts (the spec forbids it).
- Human–model agreement: no human coding in this run; the §4.2 judge is a model and this is a stated limitation.
- Anything with the Anthropic 171 audit hook.

## 10. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-10-17 (morning) | Plan written; 50 synthetic texts, 4 models (Claude / GPT / Gemini / open-weight), α / cosine / Jaccard / SD thresholds; no run | initial draft |
| 2026-10-17 (pilot, before the main run) | **Deviation D1.** `kimi-k2.6` is a reasoning model: at provider defaults its reasoning consumed the whole 8,000-token output cap with no JSON (3 of 3 pilot calls), and a 32,000-token probe showed ≈ 10,000 reasoning tokens, USD 0.049 and 126 s per call, projecting ≈ USD 37 for its 750 calls and a total ≈ USD 85 > 80. The extractor is run with Moonshot's `thinking: {type: disabled}` (probe: 47 fields parsed, see `raw/pilot/kimi-k2.6_probe_*.json`). Sampling parameters stay at provider defaults; the two Claude extractors keep adaptive thinking (their pilot cost fits). Anthropic cache TTL set to the 5-minute default so the cache-write price matches `models.json` (1.25 ×). Pilot usage: Sonnet 5.5 ≈ 1.3–1.9k output tokens, Haiku 5.5 ≈ 2.4–3.9k, gpt-6.1-sol ≈ 1.3–1.6k; all 47 fields parsed on every Claude / OpenAI pilot call. | budget rule (§3); the judge / rater reserves are unchanged |
| 2026-10-17 (evening) | **Frozen.** Thresholds replaced by the verbatim ruling of §4.1; corpus becomes three arms of 50 (synthetic, conversational LoCoMo + LongMemEval referenced by path, Pepys); models pinned to `claude-sonnet-5-5`, `claude-haiku-5-5`, `gpt-6.1-sol`, `kimi-k2.6`, judge `claude-opus-5-5` with list prices; prompts generated and recorded (Appendix A); budget USD 80 with the §3 fallback; trait fields excluded from extraction; Essential = 12 / `extensions` / recommended-vocabulary rulings applied to the draft schema first | founder rulings and overnight-run instructions; no extraction call had been made |

## Appendix A. Prompts (verbatim; files under `experiments/2026-10-17/prompts/`)

### A.1 Extraction system prompt (shared by all four extractors)

`prompts/extraction_system.txt`

~~~text
You are an extraction engine for the Emotional Data Model (EDM) v0.9 draft, Full profile (47 affective fields).

Task: read ONE source text and fill the 47 fields below. Return ONLY a JSON object, no prose and no code fences.

Rules
1. INTERPRETATION ONLY, ATTRIBUTED. Every value must be an interpretation of what the text states, attributable to a passage in it. Do not infer traits, diagnoses, hidden motives or likely feelings. If the text does not state or unmistakably paraphrase something, the field is null (or [] for arrays).
2. Fields marked STATED-ONLY in their description (self_position, kind, arousal, appraisal.attribution, bodily_sensation, meaning, turning_point, function) are null unless the subject explicitly says it.
3. Numbers: give a `value` only when you can place the text on the scale; never invent precision. `emotion.intensity.value` is how strong the felt experience is as described (0 none to 1 overwhelming). `salience.linkage_strength` is how strongly the text links this experience to other memories or themes (0 isolated to 1 central).
4. Word choice: for coded fields use one of the recommended values when it fits; otherwise a short phrase of your own (free text is accepted). Lower case except proper names.
5. If the text is a conversation, the subject is the person whose experience is being related (the User in a companion transcript; the speakers jointly in a dialogue; the client in a clinical note). Describe their stated experience, not the assistant's or clinician's.
6. Output object: one key per field path below (use the dotted path as the key, e.g. "emotion.appraisal.urgency"), in the order given, plus a final key "field_confidence": an object mapping each NON-NULL field path to your confidence 0..1 that the value is supported by the text. Return every field key even when null.

Fields (47)
## narrative
- `narrative.subject` -> string|null
    Central person, object, or theme of the experience
    Constraints: 1–5 words (e.g., "grandmother", "dad's toolbox", "childhood home")
- `narrative.trigger` -> string|null
    What triggered or initiated the emotional response
    Constraints: 1–5 words (e.g., "finding old photos", "first snow", "phone call")
- `narrative.harm` -> string|null
    Emotional pain, loss, or vulnerability present in the experience
    Constraints: 1–5 words (e.g., "abandonment", "regret", "distance", "grief")
- `narrative.drive` -> string|null
    What energized or motivated the experience
    Constraints: 1–5 words (e.g., "love", "shared laughter", "curiosity", "hope")
- `narrative.integration` -> string|null
    Connection or shift between past and present understanding
    Constraints: 1–5 words (e.g., "forgiveness", "acceptance", "returning home")
- `narrative.summary` -> string|null
    A compressed, faithful account of the experience as described by the source, preserving emotional sequence, temporal markers, and stated context without interpretation
    Constraints: 3–5 sentences
- `narrative.meaning` -> string|null
    The explicit realization or conclusion stated by the subject
    Constraints: Short sentence. Extracted, not inferred
- `narrative.identity_link` -> string|null
    A succinct expression of how the experience connects to personal identity
    Constraints: Short sentence
- `narrative.turning_point` -> true|false|null
    Marks experiences the subject explicitly identifies as life-changing or trajectory-altering at time of extraction
    Constraints: true or false; null when the subject does not say
- `narrative.arc` -> array of strings (value words)
    The story movement(s) the experience represents. A list so that a structural reading (v0.8.3 arc_type) and a trajectory reading (v0.8.3 narrative_arc) of the same memory can both be stored; order carries no meaning.
    Constraints: Each item is text + codings; EDM vocab arc/v1 unites the former arc_type and narrative_arc value sets. Free text accepted.
    Recommended values: authenticity, betrayal, bond, closure, confrontation, connection, discovery, exile, gratitude, grief, liberation, loss, moral_awakening, overcoming, reckoning, reconciliation, reflection, resistance, threshold, transformation. Other wording is accepted when none fits.
- `narrative.valence_shift` -> string|null
    Directional emotional change during the experience
    Constraints: Free text (e.g., "loss to gratitude", "fear to relief", "joy to sadness")
- `narrative.self_position` -> string|null
    The subject's own expressed lens on themselves within the story: the position they say they occupy (e.g. "the one who holds it together", "the person who finally said no"). STATED-ONLY: recorded only when the subject says it or paraphrases it unmistakably; never assigned from the plot, the emotion or an archetype catalogue.
    Constraints: Short phrase in the subject's own terms; NULL when not stated. Replaces narrative_archetype (the Mark & Pearson 12 are not used). Optional codings: McAdams imago (open label), agency / communion, Hermans I-position; all relation=related.

## emotion
- `emotion.primary` -> string|null  (the value word)
    The dominant emotional quality expressed in the experience
    Constraints: Canonical values: joy, sadness, fear, anger, wonder, peace, tenderness, reverence, pride, anxiety, gratitude, longing, hope, shame, disappointment, relief, frustration. Free text accepted.
    Recommended values: anger, anxiety, disappointment, fear, frustration, gratitude, hope, joy, longing, peace, pride, relief, reverence, sadness, shame, tenderness, wonder. Other wording is accepted when none fits.
- `emotion.secondary` -> array of strings (value words)
    Secondary emotional nuances that add depth to the primary emotion, including any complex or layered state (v0.8.3 emotion_subtone + higher_order_emotion)
    Constraints: 0-5 items; free text; each item may carry codings with a per-coding confidence
    Recommended values: anger, anxiety, disappointment, fear, frustration, gratitude, hope, joy, longing, peace, pride, relief, reverence, sadness, shame, tenderness, wonder. Other wording is accepted when none fits.
- `emotion.kind` -> string|null  (the value word)
    Whether the subject describes the affect as an episode with an object (emotion), a diffuse state without one (mood), a felt bodily quality (feeling), or a standing disposition. Stated-only; NULL when the subject does not distinguish.
    Constraints: emotion -> MFOEM:000001; mood -> MFOEM:000193; feeling -> MFOEM:000006; disposition -> MFOEM:000199
    Recommended values: disposition, emotion, feeling, mood. Other wording is accepted when none fits.
- `emotion.valence` -> {"text": string|null, "value": number in [-1, 1]|null}
    The qualitative direction of the emotional experience
    Constraints: text positive / negative / mixed; value in [-1, 1] on EmotionML fsre-dimensions#valence, populated only by an extraction that produces it (never derived from text)
    Recommended values: mixed, negative, positive. Other wording is accepted when none fits.
- `emotion.arousal` -> {"text": string|null, "value": number in [0, 1]|null}
    The stated activation level of the experience (keyed up vs calm), independent of valence and of intensity. Stated-only.
    Constraints: text low / medium / high; value in [0, 1] on EmotionML pad-dimensions#arousal; NULL when not expressed
    Recommended values: high, low, medium. Other wording is accepted when none fits.
- `emotion.intensity` -> {"text": string|null, "value": number in [0, 1]|null}
    The felt intensity of the emotional experience
    Constraints: value in [0, 1] (v0.8.3 emotional_weight carried as-is); text is an optional ordinal label
- `emotion.meta` -> string|null
    How the person relates to their own emotional state
    Constraints: Free text (e.g., "acceptance", "resistance", "curiosity", "confusion")
- `emotion.bodily_sensation` -> string|null
    Bodily or interoceptive sensations explicitly described by the subject as part of the emotional experience
    Constraints: Short phrases extracted from stated physical sensations only; NULL when not mentioned
- `emotion.temporal_profile` -> string|null  (the value word)
    The perceived temporal movement or cadence of the emotional event
    Constraints: Canonical: still, sudden, rising, fading, recurring, spiraling, dragging, suspended, looping, cyclic. looping and cyclic are deprecated (code to recurring). Free text accepted.
    Recommended values: dragging, fading, recurring, rising, spiraling, still, sudden, suspended. Other wording is accepted when none fits.
- `emotion.appraisal.urgency` -> {"text": string|null, "value": number in [0, 1]|null}
    The intensity or immediacy of the motivational state
    Constraints: text calm / elevated / pressing / acute; value in [0, 1] on EmotionML ema-appraisals#urgency, never derived from text
    Recommended values: acute, calm, elevated, pressing. Other wording is accepted when none fits.
- `emotion.appraisal.control` -> {"text": string|null, "value": number in [0, 1]|null}
    The perceived ability to act or influence the situation
    Constraints: text low / medium / high; value in [0, 1] on EmotionML scherer-appraisals#control, never derived from text
    Recommended values: high, low, medium. Other wording is accepted when none fits.
- `emotion.appraisal.attribution` -> string|null  (the value word)
    To whom or what the subject attributes the cause of the event ("I blamed myself", "it was just bad luck"). Explicit content only.
    Constraints: self -> MFOEM:000076 / EmotionML agent-self; other -> MFOEM:000078 / agent-other; chance -> MFOEM:000077 / agent-nature
    Recommended values: chance, other, self. Other wording is accepted when none fits.

## context
- `context.event` -> string|null
    Type of event or situation
    Constraints: Free text (e.g., "family gathering", "farewell", "birthday", "reunion")
- `context.event_category` -> string|null  (the value word)
    Coded companion to context.event: the content category of the event as the subject describes it.
    Constraints: Singer & Blagov / Thorne & McLean categories: relationships, life_threatening_events, recreation_exploration, achievement_mastery, guilt_shame, drug_alcohol_tobacco_use, not_classifiable (labels knowledge-reconstructed; REPORT.md section 9)
    Recommended values: achievement_mastery, drug_alcohol_tobacco_use, guilt_shame, life_threatening_events, not_classifiable, recreation_exploration, relationships. Other wording is accepted when none fits.
- `context.place` -> string|null
    Place or spatial context of the experience
    Constraints: Free text (e.g., "grandmother's kitchen", "beach", "hospital")
- `context.people` -> array of strings
    Individuals referenced in or connected to the experience
    Constraints: Names or roles, properly cased (e.g., "Sarah", "my father", "the nurse")
- `context.relationship` -> string|null  (the value word)
    The dominant relational configuration influencing the experience
    Constraints: Canonical: parent_child, grandparent_grandchild, romantic_partnership, couple, sibling_bond, family, friendship, friend, companionship, colleague, mentorship, reunion, community_ritual, grief, self_reflection, professional, therapeutic, service, adversarial. friend, couple, grief, self_reflection are deprecated. Free text accepted.
    Recommended values: adversarial, colleague, community_ritual, companionship, family, friendship, grandparent_grandchild, mentorship, parent_child, professional, reunion, romantic_partnership, service, sibling_bond, therapeutic. Other wording is accepted when none fits.
- `context.relationship_model` -> string|null  (the value word)
    Coded companion to context.relationship: the relational model the subject's account of the relationship instantiates (Fiske).
    Constraints: communal_sharing, authority_ranking, equality_matching, market_pricing, null_relation
    Recommended values: authority_ranking, communal_sharing, equality_matching, market_pricing, null_relation. Other wording is accepted when none fits.
- `context.life_stage` -> string|null  (the value word)
    The life-stage or temporal frame associated with the experience
    Constraints: Canonical: childhood, early_adulthood, midlife, late_life, recent, future, timeless
    Recommended values: childhood, early_adulthood, future, late_life, midlife, recent, timeless. Other wording is accepted when none fits.
- `context.scope` -> {"text": string|null, "direction": string|null}
    The perspective through which the experience is narrated (v0.8.3 relational_perspective) and whether the impulse is self-directed, relational or expansive beyond self (v0.8.3 directionality)
    Constraints: text: self / partner / family / friends / community / humanity; direction: inward / outward / transcendent; codings on EDM vocab scope/v1 (Bronfenbrenner nested systems as companion codes)
    Recommended values: self, partner, family, friends, community, humanity; direction one of ['inward', 'outward', 'transcendent']. Other wording is accepted when none fits.

## salience
- `salience.memory_type` -> string|null  (the value word)
    The class of memory the experience represents within personal identity
    Constraints: Canonical: legacy_artifact, fleeting_moment, milestone, reflection, formative_experience. legacy_artifact is deprecated (an object tether, not a memory type).
    Recommended values: fleeting_moment, formative_experience, milestone, reflection. Other wording is accepted when none fits.
- `salience.tether` -> {"type": string|null, "referent": string|null, "stake": string|null}
    What the experience is emotionally anchored to: its kind (v0.8.3 tether_type), the concrete referent (v0.8.3 symbolic_anchor) and what is at stake in it (v0.8.3 gravity_type)
    Constraints: type: canonical person, symbol, event, place, ritual, object, tradition, identity, self, free text accepted; referent and stake: free text
- `salience.retrieval_cues` -> array of strings
    Cues that reactivate the memory: what continues to resonate (v0.8.3 core.echo), sensory or symbolic triggers (recall_triggers) and compact retrieval hooks (retrieval_keys), concatenated in that order by migration
    Constraints: Short phrases; order carries no meaning
- `salience.themes` -> array of strings
    Adjacent themes or motifs connected to the experience
    Constraints: Concepts or emotions (e.g., "family", "tradition", "loss", "continuity")
- `salience.recurrence` -> string|null  (the value word)
    The temporal recurrence structure extracted from the experience's context, framing, and temporal markers
    Constraints: Canonical: cyclical, isolated, chronic; emerging is deprecated. Free text accepted. NULL when the pattern cannot be determined.
    Recommended values: chronic, cyclical, isolated. Other wording is accepted when none fits.
- `salience.persistence` -> {"text": string|null, "decay": string|null}
    How long the emotion is expected to stay: the perceived stickiness (v0.8.3 viscosity) and the expected decay rate (v0.8.3 temporal_decay)
    Constraints: text: low / medium / high / enduring (fluid deprecated); decay: fast / moderate / slow; codings on EDM vocab persistence/v1 (transient / short / enduring / chronic) by the fixed recode table in v09_layout.py
    Recommended values: low, medium, high, enduring; decay one of ['fast', 'moderate', 'slow']. Other wording is accepted when none fits.
- `salience.linkage_strength` -> number in [0, 1]|null
    The binding strength of the emotion within the broader emotional network
    Constraints: 0.0–1.0
- `salience.function` -> array of strings (value words)
    Why the subject says the memory matters: to guide action (directive), to define the self (self), or to connect with others (social). Multi-valued; stated-only.
    Constraints: Pillemer 1992 / Bluck 2003 memory functions
    Recommended values: directive, self, social. Other wording is accepted when none fits.
- `salience.resilience` -> array of strings
    Indicators of stabilizing or constructive emotional processing
    Constraints: 1–3 items (e.g., "acceptance", "optimism", "continuity")
- `salience.trajectory` -> string|null  (the value word)
    How the emotional state is evolving across time
    Constraints: Canonical: improving, stable, declining, integrative; emerging is deprecated
    Recommended values: declining, improving, integrative, stable. Other wording is accepted when none fits.

## motivation
- `motivation.action_tendency` -> string|null  (the value word)
    The behavioral direction or movement expressed through the emotional response
    Constraints: Canonical: explore, approach, avoid, repair, persevere, share, confront, protect, process (Frijda action tendencies applied as codes; value words unchanged)
    Recommended values: approach, avoid, confront, explore, persevere, process, protect, repair, share. Other wording is accepted when none fits.
- `motivation.need` -> string|null  (the value word)
    The foundational motivational domain guiding the individual's internal stance
    Constraints: Canonical: belonging, safety, mastery, meaning, autonomy, authenticity (SDT needs applied as codes)
    Recommended values: authenticity, autonomy, belonging, mastery, meaning, safety. Other wording is accepted when none fits.
- `motivation.temporal_focus` -> string|null  (the value word)
    The temporal direction toward which the motivational energy is oriented
    Constraints: past / present / future
    Recommended values: future, past, present. Other wording is accepted when none fits.
- `motivation.risk_posture` -> string|null  (the value word)
    The stance toward uncertainty or potential risk embedded in the moment
    Constraints: cautious / balanced / bold
    Recommended values: balanced, bold, cautious. Other wording is accepted when none fits.
- `motivation.coping` -> string|null  (the value word)
    The primary strategy used to manage or integrate the emotional experience
    Constraints: Canonical: reframe_meaning, seek_support, distract, ritualize, confront, detach, process (Ways of Coping and Gross families applied as codes). Free text accepted.
    Recommended values: confront, detach, distract, process, reframe_meaning, ritualize, seek_support. Other wording is accepted when none fits.
~~~

### A.2 Extraction user message template

`prompts/extraction_user.txt`

~~~text
Source text (id: {text_id}):

<text>
{text}
</text>

Return the JSON object now.
~~~

### A.3 Judge system prompt (Opus 5.5)

`prompts/judge_system.txt`

~~~text
You are an equivalence judge for a repeatability study. You will see, for one source text, several short free-text answers given independently for the same EDM field by different extraction runs. Your job is to group answers that say the same thing about the text, so that agreement can be measured.

Rules
1. Two answers are EQUIVALENT when a careful reader would say they describe the same referent, event, meaning or quality of the text, even if the wording differs ("the choir recording" = "recording of the winter concert"; "sister" = "my sister"). They are NOT equivalent when they pick different referents, different causes, opposite directions, or when one is substantively more specific in a way that changes what is claimed.
2. null / empty answers form their own group ("null").
3. Judge the answers against the source text when it helps; never rewrite them.
4. Return ONLY JSON: {"fields": {"<field path>": {"groups": [[<answer index>, ...], ...], "note": "<one short clause, optional>"}, ...}}. Every answer index must appear in exactly one group. Answer indices are the integers shown before each answer.
~~~

### A.4 Judge user message template

`prompts/judge_user.txt`

~~~text
Source text (id: {text_id}):
<text>
{text}
</text>

Answers to judge, per field (index: answer):
{answers_block}

Return the JSON object now.
~~~

### A.5 Task (b) rater system prompt

`prompts/rater_system.txt`

~~~text
You are reading an Emotional Data Model (EDM) v0.9 artifact extracted from a text you cannot see. Four fields have been blanked. Fill them from the artifact alone.

Return ONLY JSON: {"narrative.arc": <one value word or short phrase>, "salience.trajectory": <one of improving, stable, declining, integrative, or your own word>, "motivation.need": <one of belonging, mastery, autonomy, safety, meaning, authenticity, or your own word>, "narrative.valence_shift": <short phrase, e.g. "dread to relief">}

Recommended arc values: authenticity, betrayal, bond, closure, confrontation, connection, discovery, exile, gratitude, grief, liberation, loss, moral_awakening, overcoming, reckoning, reconciliation, reflection, resistance, threshold, transformation. Use null where the artifact gives no basis.
~~~

### A.6 Task (b) rater user message template

`prompts/rater_user.txt`

~~~text
Artifact:
{artifact_json}

Return the JSON object now.
~~~

