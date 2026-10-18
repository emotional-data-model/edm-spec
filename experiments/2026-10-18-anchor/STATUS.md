# STATUS — human anchor on GoEmotions (2026-10-18 night, Phase B)

**Nothing pushed. `schema/` and `examples/` untouched. The founder's archive was not used.** Pre-registration `docs/discovery/ontology-crosswalk-2026-10/experiment-plan-anchor.md`, frozen by commit `5ac5169` before any call; no deviation (`levers_anchor.json` absent).

## Run

| Gate | Result |
|---|---|
| Freeze before any call | **Passed** (`5ac5169`) |
| Sample | 1,000 of 46,826 eligible comments, stratified by human majority label (seed 20261018), sha256 `8f4cd1e4…`; 82 raters in the release, 84.4 % single-label annotations |
| Pilot | 3 calls, USD 0.014; projection USD 2.03 ≤ cap 10 → no lever |
| Extraction | 450 calls (3 models × 3 repeats × 50 batches of 20), **USD 2.14 of the 10 cap**, 1,581 s at concurrency 3; 0 transport failures, 0 provider mismatches; Sonnet 4 unparsable calls + 80 missing ids (0.9 % of its item-repeats), gpt-oss 3 missing ids, Gemini none; every comment has ≥ 1 valid repeat for every model |
| Scoring | `scoring/anchor_scoring.json`, `RESULTS.md` (`scripts/score_anchor.py`); frozen mapping `G2E`, 19-category space |

## The sentence (RESULTS.md §1)

Human–human range = IQR of rater-vs-rest κ across the 31 raters with ≥ 30 single-label items.

| Field | human–human range (median) | Claude Sonnet 5.5 | Gemini 4 Argon | gpt-oss-120b |
|---|---|---|---|---|
| `emotion.primary` | [0.25, 0.43] (0.34) | κ 0.23 → **below** | κ 0.27 → **within** | κ 0.25 → **below** (by 0.002) |
| `emotion.valence` | [0.37, 0.53] (0.48) | κ 0.35 → **below** | κ 0.41 → **within** | κ 0.39 → **within** |

So, per field: **`primary`: model–human κ is at or just below the lower edge of the human–human range** (two of three below, one within; all three within 0.02 of Q1). **`valence`: model–human κ is within the human–human range for two of three models** and just below it for Sonnet. Against *individual* raters every model is well below what a rater reaches against the rest (primary medians 0.16–0.19 vs 0.34; valence 0.29–0.34 vs 0.48): the models agree with the consensus about as well as a weak-to-median rater does, and with any single rater less than raters agree with each other.

Repeatability (Fleiss κ, 3 repeats): primary Sonnet 0.65, Gemini 0.79, gpt-oss 0.67; valence 0.77 / 0.85 / 0.76. The 20-comment batch context differs per repeat, which the run-3 single-text repeats did not have; the lower Sonnet figure comes with 59 modal ties.

**Predictions: none of P1–P5 held.** P1 (all below) fails on Gemini; P2 (all within or above on valence) fails on Sonnet; P3 (S ≥ G ≥ O) fails: Gemini is highest on both fields; P4 (repeat ≥ 0.70 for S and G) fails on Sonnet; P5's primary clause holds (every model's vs-rater median below the human median) but its valence clause fails.

**Where the disagreement is (RESULTS.md §4):** the `other` ↔ `neutral` boundary (the eight unmapped GoEmotions labels — amusement, approval, confusion, disapproval, disgust, excitement, grief, realization — against no emotion), `wonder` (surprise / curiosity) read as `other` or `neutral`, and `tenderness` / `reverence` (love, caring, admiration) read as `joy`. These are mapping seams of the EDM vocabulary against GoEmotions, not noise: an EDM extractor given the 17 values has no word for amusement, approval or disgust and puts them in free text (→ `other`) or in `joy` / `frustration` / `anger`.

## What this does and does not say

It gives the first human anchor for two comparable-tier fields: model agreement with a human consensus on a short-text emotion label is at the lower edge of inter-rater agreement for the label and inside it for valence. It does not re-class any field (the fields are not re-ruled here), does not add GoEmotions to the crosswalk, and says nothing about the narrative fields or about long texts. The spare budget (USD 7.86 of 10) was not spent on extra repeats or models, as the plan allowed none.

## Founder actions

1. Read the sentence and decide whether `emotion.primary`'s class should carry a `human_anchor` annotation (κ vs human majority 0.23–0.27; human range [0.25, 0.43]) — a ruling, not done here.
2. Whether the three mapping seams (`other`/`neutral`, `wonder`, `tenderness`/`reverence`) warrant vocabulary notes in the draft fragment (discovery only).
3. Push (founder-only).
