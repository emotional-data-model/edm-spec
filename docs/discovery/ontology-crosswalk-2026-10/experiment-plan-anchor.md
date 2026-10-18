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
