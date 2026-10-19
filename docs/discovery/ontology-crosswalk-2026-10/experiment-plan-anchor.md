# Pre-registration — human anchor on GoEmotions (2026-10-18)

**Status: frozen by the commit `anchor pre-registration frozen` before any call; executed the same night under Phase B of the founder's overnight instruction (cap USD 10). Deviations, if any, are logged in `experiments/2026-10-18-anchor/levers_anchor.json` and in §10 below.**

## 1. Question

Runs 1–3 measured *extractor–extractor* agreement on EDM fields: repeatability within a model and agreement with a voting majority of models. None of them says how either figure relates to *human* agreement on the same kind of judgement. This run anchors the two fields with the clearest human counterpart, `emotion.primary` and `emotion.valence`, against a public corpus with individual rater annotations: **is a model's agreement with the human majority inside the range of agreement that humans reach with each other on the same items?**

The answer is one sentence per field, written in `RESULTS.md` §1: *"model–human κ is / is not within the human–human range"*, with the figures beside it.

## 2. Corpus

GoEmotions (Demszky et al. 2020; `google-research/goemotions`, Apache 2.0), the **full release with individual rater annotations** (`data/full_dataset/goemotions_{1,2,3}.csv`: one row per rater × comment, 27 emotion labels + `neutral`, 82 raters, 58,011 comments). Downloaded 2026-10-18; sha256 of the three files recorded in `experiments/2026-10-18-anchor/data/sample_stats.json`; the raw files are not committed (`data/goemotions_raw/` is gitignored).

**Eligibility** (`scripts/sample_goemotions.py`): ≥ 3 raters on the comment; no rater flagged `example_very_unclear`; a unique plurality label with ≥ 2 votes (a rater's vote counts once per label they chose). 46,826 of 58,011 comments are eligible (excluded: tied plurality 5,722; plurality below two votes 3,001; fewer than three raters 662; the rest flagged unclear). The **human majority label** of a comment is its plurality label.

**Sample:** 1,000 comments, stratified by majority label, allocation proportional to the eligible count per label with a floor of 15 (capped at the label's eligible count), seed 20261018, remainder by largest remainder. Result: `neutral` 206, `admiration` 61, `gratitude` 51, `approval` 45, `amusement` 42, `love` 39, `annoyance` / `curiosity` / `disapproval` 38, … `grief` / `nervousness` / `pride` / `relief` 16 (full table in `data/sample_stats.json`). Written to `data/sample.json` (id, text, subreddit, majority label and vote count, rater count, every rater's label set); sha256 of the sample `8f4cd1e4509d27388c65ff8842809e26b568a347a2bce061b348a60d668618ac`. 84.4 % of the rater annotations on eligible comments carry exactly one label.

The founder's own archive is **not used** in this run.

## 3. Fields and the frozen mapping

Two fields of the v0.9 draft, both comparable-tier after run 3: `emotion.primary` (free text, recommended vocabulary of 17: anger, anxiety, disappointment, fear, frustration, gratitude, hope, joy, longing, peace, pride, relief, reverence, sadness, shame, tenderness, wonder) and `emotion.valence.text` (positive / negative / mixed).

**Mapping GoEmotions → EDM (`G2E`), from the crosswalk row `constellation.emotion_primary` (`crosswalk.csv`, GoEmotions column; exact and related links as verified there):**

| GoEmotions | EDM `emotion.primary` | crosswalk link |
|---|---|---|
| joy | joy | exact |
| sadness | sadness | exact |
| fear | fear | exact |
| anger | anger | exact |
| pride | pride | exact |
| gratitude | gratitude | exact |
| relief | relief | exact |
| disappointment | disappointment | exact |
| nervousness | anxiety | exact |
| optimism | hope | exact |
| desire | longing | related |
| surprise, curiosity | wonder | related |
| admiration | reverence | related (admiration is listed under both wonder and reverence; reverence is its sole single-target link) |
| caring, love | tenderness | related |
| embarrassment, remorse | shame | related |
| annoyance | frustration | related (frustration's other link, anger, is taken by anger's exact match) |
| neutral | neutral | sentiment grouping |
| amusement, approval, confusion, disapproval, disgust, excitement, grief, realization | **other** | no EDM counterpart |

The reverse direction (`E2G`) is the same table read back; the one EDM value with no GoEmotions counterpart, **`peace`, maps to `other`**. The mapping is written as data in `scripts/score_anchor.py` (`G2E`) and must not change after the freeze.

**Model label normalisation** (`norm_primary`): lower-case, trimmed; a value in the 17 → itself; `null`, empty, "none", "neutral" → `neutral`; anything else (free text the field permits, including a GoEmotions word such as "disgust") → `other`. **Scoring space for `primary`: 19 categories** (17 + `neutral` + `other`); `peace` is kept as its own category on the model side (a human label never maps to it, so it can only lower agreement).

**Valence:** the human valence of a label is its GoEmotions sentiment group (`sentiment_mapping.json`: positive → `positive`, negative → `negative`, ambiguous → `mixed`, `neutral` → `neutral`). Model valence: positive / negative / mixed as given; `null` or empty → `neutral`; anything else → `other` (never expected). Scoring space: 4 categories (+ `other` if it occurs).

## 4. Extractors, prompt and calls

Through OpenRouter, pinned as in run 3 (`experiments/2026-10-18-run3/models.json`): **Claude Sonnet 5.5** (`anthropic/claude-sonnet-5.5` @ `anthropic`, gateway default reasoning — the endpoint refuses reasoning off, run 3 R3-D2), **Gemini 4 Argon** (`google/gemini-4-argon` @ `google-vertex/global`, defaults), **gpt-oss-120b** (`openai/gpt-oss-120b` @ `deepinfra/bf16`, `reasoning: {effort: low}` as run 3 lever 1). `response_format: json_object`, `max_tokens` 8,000, provider pinned with `allow_fallbacks: false`, provider name recorded per record and a mismatch is a failed call.

**One shared system prompt** (`prompts/anchor_system.txt`): the two field definitions verbatim from the draft fragments (`emotion.primary` description, recommended vocabulary and "free text accepted"; `emotion.valence.text` positive / negative / mixed), the EDM rule that fields record what is *expressed* in the text, not inferred, `null` for `primary` when no emotional quality is expressed, and the output shape: a JSON object keyed by comment id, each value `{"primary": string|null, "valence": "positive"|"negative"|"mixed"|null}`. The user message carries **a batch of 20 comments** (`id: text`, one per line). The three models receive identical messages.

**Batches:** 50 batches of 20 per repeat; batch composition is a seeded shuffle of the 1,000 ids that differs per repeat (seed 20261018 + repeat), so no comment sits with the same neighbours twice and the three repeats are three contexts. **3 repeats × 50 batches × 3 models = 450 calls.** Checkpointed per call to `raw/<arm>.jsonl` (batch ids, raw text, parsed answers, usage, cost, provider, reasoning tokens); a re-run skips completed (repeat, batch) jobs. A comment missing from a parsed answer, or an unparsable call, is a **missing repeat** for every comment in the batch (never re-sampled). An OpenRouter 429 after six attempts with backoff is a transport failure and is re-requested once (run 3 R3-D3).

**Pilot:** one batch per model (3 calls, repeat 1, batch 1) → projection; the pilot records are kept and count. Levers in order if the projection exceeds the cap: (1) repeats 3 → 2; (2) drop Gemini 4 Argon. **Cap USD 10** on this run's spend (`spend_anchor.json`); the runner stops checkpointed at the cap.

## 5. Measures (all frozen; `scripts/score_anchor.py`)

Per model, **modal label** per comment over the valid repeats (ties → the label of the lowest repeat; tie rate reported); a comment with no valid repeat is excluded from that model's κ (count reported).

1. **Model vs human majority, `κ_maj`:** Cohen's κ between the model's modal label and the human majority label (`G2E`), over all comments with a modal label (19-category space; raw agreement beside).
2. **Model vs each rater, `κ_rater(m, r)`:** for each rater *r* with ≥ 30 **single-label** annotations in the sample, Cohen's κ between the model's modal label and *r*'s label (`G2E`) on those comments. Reported per rater, summarised as median and IQR across raters.
3. **Human–human, rater vs rest, `κ_rest(r)`:** for each rater *r* (same ≥ 30 rule), Cohen's κ between *r*'s single label and the plurality of the *other* raters on the comment (unique plurality with ≥ 2 votes among the others; otherwise the comment is skipped for *r*). This is the human analogue of measure 1: one annotator against the consensus of the rest. **The human–human range is the interquartile range [Q1, Q3] of `κ_rest(r)` across raters**; its median, min and max are reported beside it, as is the pooled κ over all (rater, comment) pairs.
4. **Human–human, pairwise, `κ_pair`:** Cohen's κ pooled over every (comment, rater *i*, rater *j*) with single labels from both (one contingency table), and the distribution across rater pairs sharing ≥ 30 comments — reported as context, not used for the sentence.
5. **Repeatability:** Fleiss' κ across the three repeats per model (the run-1 statistic), reported beside.
6. **Valence:** measures 1–5 with the labels collapsed to the 4-category valence space; the human majority valence is the sentiment group of the majority label.

**The sentence**, per field and per model: *"model–human κ is within the human–human range"* when `κ_maj` ∈ [Q1, Q3] of `κ_rest`; *"above"* when `κ_maj` > Q3; *"below"* when `κ_maj` < Q1. RESULTS.md §1 writes it for each of the three models and both fields; the headline uses the median model.

## 6. Predictions (frozen)

- **P1.** For `emotion.primary`, every model's `κ_maj` is **below** the human–human range. Reason: the EDM vocabulary is not the raters' vocabulary; eight GoEmotions labels collapse to `other` and four EDM values absorb several labels each, so part of the raters' consensus is unrecoverable from the field.
- **P2.** For `valence`, every model's `κ_maj` is **within or above** the human–human range.
- **P3.** Ordering on `primary` `κ_maj`: Sonnet 5.5 ≥ Gemini 4 Argon ≥ gpt-oss-120b.
- **P4.** Repeatability (Fleiss' κ, 3 repeats) on `primary` ≥ 0.70 for Sonnet 5.5 and Gemini 4 Argon.
- **P5.** Model vs each rater: the median of `κ_rater(m, r)` across raters is **below** the median of `κ_rest(r)` for every model on `primary` and **not below** it for at least one model on `valence`.

## 7. Cost

450 calls of ≈ 1,100 prompt tokens and ≈ 400 output tokens (Sonnet adds its mandatory reasoning, ≈ 500–1,500 tokens per call in run 3). Projection: Sonnet ≈ USD 4.5, Gemini ≈ USD 3.0, gpt-oss-120b ≈ USD 0.1; ≈ USD 8 of the **USD 10 cap**. No judge.

## 8. What this run does not do

It does not change any field's class or profile (the fields are not re-ruled on a human anchor; that is a decision for the founder with the figures in hand). It does not use the founder's archive. It does not add GoEmotions to the crosswalk as a coding system.

## 9. Files

`experiments/2026-10-18-anchor/`: `data/sample.json`, `data/sample_stats.json`, `prompts/anchor_system.txt`, `prompts/anchor_user.txt`, `scripts/sample_goemotions.py`, `scripts/run_anchor.py`, `scripts/score_anchor.py`, `models_anchor.json`, `levers_anchor.json`, `spend_anchor.json`, `raw/`, `scoring/`, `RESULTS.md`, `STATUS.md`.

## 10. Deviations

None at freeze. Logged here and in `levers_anchor.json` if any arise.

---

# Anchor-2 — wider vocabulary, content cues, prompt-length control (pre-registration, 2026-10-19)

**Status: frozen by the commit `anchor-2: pre-registration frozen (after R31 d5ace00)` before any call (hash recorded in §A2.11 after the commit). Hard cap USD 11 on OpenRouter for the whole run. Branch `discovery/ontology-crosswalk`; nothing pushed.** Depends on R31 (`lexical-familiarity.md`, commit `d5ace00`): the 18 MFOEM additions have never been offered in a prompt, so arm A is their first test. Files: `experiments/2026-10-19-anchor2/` (`mapping.json`, `models_anchor2.json`, `prompts/`, `scripts/run_anchor2.py`, `scripts/score_anchor2.py`, `levers_anchor2.json`, `spend_anchor2.json`, `raw/<arm>/`, `scoring/`, `RESULTS.md`).

## A2.1 Question

Anchor-1 put every model's `emotion.primary` agreement with the human majority at or just below the human–human range, and located the disagreement on three seams of the 17-word vocabulary against GoEmotions (the eight labels with no EDM value; `wonder`; `tenderness` / `reverence`). Three questions, one arm each: (A) does the v0.9 wider recommended vocabulary (17 + 18 MFOEM additions, `REPORT.md` §5) close the seams; (B) does reading guidance from the content subset of `cues-v1.md` move agreement beyond the vocabulary effect; (C) is any B effect attributable to prompt length rather than content.

## A2.2 Corpus and extractors

Identical to anchor-1 (§2, §4): the same 1,000 GoEmotions comments (`experiments/2026-10-18-anchor/data/sample.json`, sha256 `8f4cd1e4…`), the same three extractors pinned at the same endpoints and prices (`models_anchor2.json` carries `models_anchor.json` verbatim; gpt-oss-120b `reasoning: {effort: low}`, the other two at the gateway default), the same seeded batches of 20 (seed 20261018 + repeat), **3 repeats**, `response_format: json_object`, provider pinned with `allow_fallbacks: false`, provider mismatch = failed repeat. **`emotion.primary` only**: the output object per comment is `{"primary": string|null}`; `emotion.valence` is not requested (a difference from anchor-1's prompt, recorded as a known confound of the before/after comparison: the before column comes from a two-field prompt). **9 × 150 = 1,350 calls** (three arms × three extractors × 150), plus one pilot batch per extractor per arm (9 calls, kept, counted).

## A2.3 Cue partition (every `cues-v1.md` entry, by name)

**Content cues — can appear in a single short un-timestamped comment (23).** `rl:over-explaining`, `rl:unasked-denial`, `rl:counting`, `rl:trailing-list`, `rl:unfinished`, `rl:hedge`, `rl:minimising`, `rl:abstraction`, `rl:agentless-passive`, `rl:register-shift`, `rl:joke-at-weight`, `rl:meta-comment`, `rl:repetition`, `rl:self-repair`, `rl:tense-shift-person`, `rl:pronoun-distance`, `rl:slip`, `rl:precise-detail`, `rl:counterfactual`, `rl:intensifier-stack`, `rl:open-coda`, `rl:unprompted-contrast`, `rl:explicative-overload`. Several are defined against a within-text norm (`hedge`, `minimising`, `abstraction`, `pronoun-distance`, `register-shift`); a short comment can still show them against its own other clauses, and the block says so. They are the arm-B block, `prompts/cue_block.txt`, each as code, one-line definition and what it licenses for `primary` ("content hypothesis" or "weight only"), with the attribution rule restated.

**Conversational cues — need a prior turn, timing, or other entries; not testable on this corpus; tested in run 4 on conversational text (`experiment-plan-run4.md`) (12).**

| Cue | Exclusion reason |
|---|---|
| `rl:delayed-reply` | needs timestamps and the writer's own reply gaps |
| `rl:going-quiet` | needs a raised topic and a later turn where its closure is absent |
| `rl:preface` | needs the question the preface delays the answer to |
| `rl:minimal-answer` | needs the question and the writer's answer length elsewhere |
| `rl:late-return` | needs an earlier closed topic and a later return |
| `rl:recurring-subject` | needs several parts of a text or several entries |
| `rl:rereading` | needs an earlier entry or passage to refer back to |
| `rl:dropped-name` | needs the writer's naming practice across a text |
| `rl:we-shift` | needs a pronoun regime for a relationship established across a text |
| `rl:topic-change` | needs an open prior topic and marked transitions elsewhere |
| `rl:deflection` | needs the question that goes unanswered |
| `rl:absent-party` | needs an earlier span that makes the absence noticeable |

## A2.4 Arms

- **A — wider vocabulary.** `prompts/system_A.txt`: the anchor-1 system prompt with the field definition's recommended values extended to the 35 words (17 v0.8.3 + 18 MFOEM additions in `REPORT.md` §5 order), "free text accepted", `primary` only. 300 tokens (tiktoken `o200k_base`).
- **B — A + content cues.** `prompts/system_B.txt` = A + `prompts/cue_block.txt` (1,053 tokens) as reading guidance. 1,353 tokens.
- **C — A + length-matched irrelevant text.** `prompts/system_C.txt` = A + `prompts/control_block.txt` (1,044 tokens; 99.1 % of the cue block, within the 5 % bound; `cl100k_base`: 1,046 vs 1,056). The control is a **structural excerpt of W3C EmotionML 1.0** rendered from the fetched construct record (`sources/group_d_machine.json`, `w3c_emotionml_1_0`: element model, attribute conventions, reference roles, the dimension / appraisal / action-tendency vocabularies, a minimal document, conformance). **The category vocabularies (big6, everyday, OCC, FSRE, Frijda emotion-word lists) are deliberately excluded** so that the control carries no emotion labels that could prime `primary`; appraisal names (desirability, blame, urgency …) remain and are noted. The excerpt is headed "not used by this task". 1,344 tokens total. Vendor tokenisers differ from tiktoken; the gateway's reported prompt tokens per arm are recorded in RESULTS.md beside.

Arm order A → B → C, each arm run to completion before the next; same user message as anchor-1 (`prompts/user.txt`).

## A2.5 The EDM → GoEmotions mapping for the full vocabulary (recorded before any call; `mapping.json`)

`E2G`: each of the 35 words → one **primary** GoEmotions label (null = no counterpart, scored `other` at the Ekman and valence grains), the crosswalk relation of that link, and further **related** labels. The 17 are the anchor-1 table read back (`wonder` → surprise primary, curiosity and admiration related; `tenderness` → caring primary, love related; `shame` → remorse primary, embarrassment related; `peace` → none). The 18 additions: `disgust` → disgust, `surprise` → surprise, `love` → love, `grief` → grief, `embarrassment` → embarrassment, `amusement` → amusement (all exact); `contempt` → disapproval, `guilt` → remorse, `regret` → remorse, `interest` → curiosity, `awe` → admiration, `compassion` → caring (related); `nostalgia`, `loneliness`, `envy`, `boredom`, `contentment`, `trust` → none (related labels listed; `other` at coarser grains).

`G2E35` (the fine-grain human side): each GoEmotions label → the one EDM word whose E2G primary it is, exact-match additions taking their own label: surprise → `surprise`, love → `love`, embarrassment → `embarrassment`, disgust → `disgust`, grief → `grief`, amusement → `amusement`, curiosity → `interest`, disapproval → `contempt`; the rest as anchor-1; approval, confusion, excitement, realization → `other`. The anchor-1 `G2E` (17) is kept in `mapping.json` for reference.

## A2.6 Scoring (frozen; `scripts/score_anchor2.py`)

Per arm and model: modal label per comment over the valid repeats (anchor-1 rule; ties → lowest repeat, counted). Model normalisation: lower-case trimmed; one of the 35 → itself; null / empty / "none" / "neutral" → `neutral`; anything else → `other`. **Coverage** = comments with a valid output from the arm (every comment has a human majority by construction); **null is an answer** (`neutral`), never a gap.

**Three grains.** *Fine*: EDM 35-word space + `neutral` + `other`; human side via `G2E35`. *Ekman (6 + neutral + other)*: human label → its GoEmotions Ekman group (`ekman_mapping.json`); model word → E2G primary → Ekman group. *Valence (positive / negative / ambiguous / neutral + other)*: the GoEmotions sentiment grouping, both sides via the same path.

**Strict κ**: Cohen's κ, model modal vs human majority, as anchor-1; and vs each rater with ≥ 30 single-label items (median, IQR). **Graded κ**: weighted Cohen's κ with agreement weights exact 1 / related 0.5 / different 0 (κ_w = (p_o,w − p_e,w) / (1 − p_e,w)). *Related* at the fine grain: the two EDM words are linked by an E2G primary-or-related label (crosswalk relations) or their E2G primaries share an Ekman group; at the Ekman grain: the two groups share a sentiment group; at the valence grain: ambiguous vs positive or negative. `neutral` and `other` are related to nothing.

**Human–human range** per grain: the rater-vs-rest IQR recomputed on the same raters in each grain's space (strict and graded), reported beside; **P1 uses the frozen anchor-1 figure [0.25, 0.43]** as written.

**Seam subset**: the 1,000 comments whose human majority label is one of amusement, approval, confusion, disapproval, disgust, excitement, grief, realization (no v0.8.3 value) or surprise, curiosity (`wonder`), caring, love (`tenderness`), admiration (`reverence`); every measure is reported overall, on the seam subset and off it.

**Before column**: the anchor-1 raw records re-scored under exactly this scheme (`G2E35`, three grains) so that before and after differ only in the arm; anchor-1's published κ (17-word `G2E`) is quoted beside for continuity.

**Exploratory, not a test**: for each of the 18 additions, per arm and model, binary category κ, recall and precision against the `G2E35` human side (the R31 statistic), for a later ranking.

## A2.7 Predictions (frozen)

- **P1.** Arm A lifts fine-grain strict κ vs the human majority into the human range **[0.25, 0.43]** for **≥ 2 of 3** models, and the lift (A − before) is larger on the seam subset than off it for ≥ 2 of 3. No per-word expectation from lexical familiarity: R31 found no detectable relation, and the MFOEM additions have never been offered in a prompt, so this is their first test; per-word κ and recall for the additions are recorded in RESULTS.md as exploratory.
- **P2.** On the seam subset (fine, strict), **B > C ≈ A**: B exceeds both A and C by ≥ 0.05 and |C − A| ≤ 0.05, for ≥ 2 of 3 models.
- **P3.** **C ≈ A everywhere**: |C − A| ≤ 0.05 (strict) at every grain, overall and on the seam subset, for every model.
- **P4.** **Graded κ > strict κ** at every grain, for every arm and model (overall).

Tolerance 0.05 throughout.

## A2.8 Disconfirmations (frozen)

- **C ≈ B** on the seam subset (|B − C| ≤ 0.05, ≥ 2 of 3 models): the B lift is prompt length, not reading.
- **Uniform B − A lift off the seams** (≥ 0.05 off-seam and not smaller than the seam lift, ≥ 2 of 3): priming, not reading.
- **Flat B** (|B − A| ≤ 0.05 strict at every grain, overall and seam, every model): evidence about content cues on this corpus only (short public comments), not about the catalogue.

## A2.9 Cost and levers

Anchor-1 cost USD 2.14 for 450 calls (Sonnet 1.12, Gemini 0.99, gpt-oss 0.03) with a ≈ 400-token system prompt. Arm A ≈ USD 2.3; arms B and C add ≈ 1,050 system tokens per call (≈ USD 0.3 per arm per closed-weight model, less if cached): ≈ USD 2.9 each. Projection ≈ USD 8.5 of the **hard cap USD 11** (`spend_anchor2.json`, shared across arms; the runner stops checkpointed at the cap). Pilot per arm (one batch per extractor) → projection; levers in order if the projected total exceeds the cap: (1) repeats 3 → 2 for the arm not yet run; (2) drop Gemini 4 Argon for that arm. Levers are recorded in `levers_anchor2.json` and in §A2.12.

## A2.10 What this run does not do

No field is re-classed; no schema file changes; the founder's archive is not used; the conversational cues are not tested here; no judge. Nothing is re-classified after the run: any deviation goes in §A2.12 and RESULTS.md §7 with its reason.

## A2.11 Freeze

Frozen at commit: _(hash recorded after the freeze commit)_.

## A2.12 Deviations

None at freeze.
