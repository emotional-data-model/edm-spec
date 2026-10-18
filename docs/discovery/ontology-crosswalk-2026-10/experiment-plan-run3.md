# Run 3 — vendor breadth on the comparable tier (PRE-REGISTRATION DRAFT; NOT RUN, NOT FROZEN)

Discovery output, branch `discovery/ontology-crosswalk`, drafted 2026-10-18 (later) on the founder's instruction of that date, under rulings R9 and R17 of `rulings-2026-10-18.md` (*ruling under delegation, veto by exception*). **No call has been made.** Freezing is a founder action: a commit titled `run 3 pre-registration frozen` before the first extraction call, as for runs 1 and 2. After the freeze this file changes only in §12 (deviations).

## 0. What run 3 is

Runs 1 and 2 classed every v0.9 field by how three voting extractors (Claude Sonnet 5.5, gpt-6.1-sol, Kimi K2.6) behave on 150 texts, and R17 made the profiles follow that class: the 19 fields classed **comparable** are the Essential profile. "Comparable" so far means *comparable across those three vendors*. Run 3 asks whether it holds across the market: the same 150 texts and the same thresholds, the 19 comparable-tier fields only, six further models from six further vendor lines pinned through one gateway (OpenRouter), five repeats each. No new field, no new text, no new threshold.

What run 3 decides (§7): per model × field, whether the model repeats the field and agrees with the run-1 / run-2 majority; per field, whether "comparable" holds across ≥ 5 of 9 models in total (the three voters plus the six new arms). What it does not decide: profile membership directly (R17 derives it from class; §7 states the pre-registered recommendation if a field fails, and the founder rules).

## 1. Questions

| # | Question | Decides |
|---|---|---|
| Q1 | Per model and field: repeatability within the model over five repeats (frozen thresholds) | whether the model can extract the field at all |
| Q2 | Per model and field: agreement of the model's answer with the **majority of the three voters** on the same text (run-1 outputs; run-2 Arm B for `harm`) | whether the model reads the field the way the voting tier does |
| Q3 | Per field: does "comparable" hold across ≥ 5 of 9 models? | whether the Essential tier is a market claim or a three-vendor claim |
| Q4 | Do the open-weight arms behave like the reported cheap tier (Haiku 5.5, `gpt-5.4-mini`) or like the voting tier? | the pre-registered prediction (§7); cost-tier guidance for implementers |

## 2. Corpus (unchanged)

The 150 texts of runs 1 and 2, byte-identical (`experiments/2026-10-17/corpus/corpus_manifest.jsonl`, sha256 per text): synthetic 50, conversational 50 (LoCoMo / LongMemEval, referenced by path, never copied), Pepys 50. The run-3 manifest is a copy with the run date changed; any sha256 mismatch at run time aborts the run.

## 3. Models (pinned by exact OpenRouter ID; list prices read from `https://openrouter.ai/api/v1/models` on 2026-10-18, USD per million tokens, input / output; cache-read price in brackets where the listing gives one)

| Arm | Vendor line asked for | Pinned ID | Listed | Price in / out (cache read) | Weights | Note |
|---|---|---|---|---|---|---|
| N1 | Gemini, current pro | `google/gemini-4-argon` | 2026-10-13 | 2.00 / 10.00 (0.10); reasoning tokens billed at 10.00 | closed | Google's current flagship reasoning model; no model named `*-pro` is newer than `google/gemini-3.1-pro-preview` (2026-02-19; 2.00 / 12.00), which is the alternative if the founder wants the "Pro"-named line |
| N2 | DeepSeek, current chat | `deepseek/deepseek-v4-pro-0813` | 2026-08-12 | 0.66 / 1.98 (0.022) | open-weight (to confirm from the vendor's model card at freeze) | GA release of the V4 Pro general line; `deepseek/deepseek-v4.1-flash-1017` (2026-10-17; 0.15 / 0.60) is the newer *flash* snapshot, served as `deepseek-flash`, and is the alternative |
| N3 | Qwen, largest current | `qwen/qwen3.8-2.4t-a95b` | 2026-08-12 | 2.00 / 6.00 (0.25) | open-weight (stated in the listing: 2.4 T total, 95 B active; the open-weight variant of Qwen3.8 Max) | `qwen/qwen3.8-max-prime` (4.00 / 12.00) is the same Max line served faster, not larger |
| N4 | Llama, largest current | `meta-llama/llama-4-maverick` | 2025-04-05 | 0.1875 / 0.6525 (0.05) | open-weight | 128-expert MoE, 17 B active; no larger Llama is listed; no reasoning parameter |
| N5 | Mistral Large | `mistralai/mistral-large-4-0` | 2026-10-06 | 0.68 / 2.09 (0.07) | to confirm at freeze (Large 3 was Apache 2.0) | current Large |
| N6 | one more (chosen here) | `openai/gpt-oss-120b` | 2025-08-05 | 0.15 / 0.60 (0.075) | open-weight (stated in the listing; 117 B MoE, 5.1 B active) | chosen because it gives a **within-vendor open / closed contrast** with the voter `gpt-6.1-sol`, which isolates "open-weight" from "vendor" for Q4, and because it is cheap. Alternatives considered and not chosen: `x-ai/grok-4.7` (new closed vendor; 2.00 / 6.00, ≈ USD 8 more), `z-ai/glm-5.3` (open-weight reasoning model; 0.079 / 4.80, reasoning tokens make its cost unbounded here) |
| Ref | cheap-tier reference, **reported, not one of the 9** | `claude-haiku-5-5` (Anthropic direct, as runs 1–2) | — | 0.10 / 0.50 (cache 0.01) | closed | re-run under the run-3 prompt so that the cheap-tier comparison in Q4 is made under the same 19-field framing, not against run-1 figures from a 47-field prompt |
| Judge | equivalence judge | `claude-opus-5-5` (Anthropic direct) | — | 4.00 / 20.00 (0.20) | — | never an extractor; `output_config.effort = "low"` as in runs 1–2; rules 1–5 |

Gateway rules (fixed now): base URL `https://openrouter.ai/api/v1`, key `OPENROUTER_API_KEY` (present in `.env`); OpenAI-compatible chat completions through the run-1 `Provider` class with a new provider kind `openrouter`. OpenRouter routes one model ID to several hosting providers, which for open-weight models can mean different quantisations: at freeze the `/models/{id}/endpoints` listing is read, one hosting provider per model is pinned in `models.json` (`provider.order = [that provider]`, `allow_fallbacks = false`), and the `provider` field of every response is recorded; a response from any other provider is logged as a failed repeat, never re-sampled. Sampling: provider defaults (no temperature, top_p or effort set), fresh context per call, as runs 1–2; Anthropic cache for the two direct models at the 5-minute TTL. Prices: OpenRouter bills the hosting provider's price, which the listing shows for the top provider; `models.json` pins the listed price and the pilot measures the actual.

**Calls.** Extraction: 150 texts × 5 repeats × 6 arms = **4,500**, plus the Haiku reference 750 = 5,250. Judge: §5. No task (a) / (b).

## 4. Fields and prompt

**Fields (19, the R17 comparable tier; `scripts/v09_layout.py` `PROFILES_09['essential']`)**, with the shape under which each is scored (`experiment-plan.md` §4.2):

| Shape | Fields | Scored by |
|---|---|---|
| C coded (text) | `emotion.primary`, `emotion.valence`, `emotion.appraisal.attribution`, `context.event_category`, `context.relationship`, `context.scope` (text), `salience.tether` (type), `motivation.action_tendency`, `motivation.need`, `motivation.temporal_focus`, `motivation.coping` | Fleiss κ, **no judge** |
| CL coded list | `salience.function` (first element) | Fleiss κ on the first element, no judge |
| B boolean | `narrative.turning_point` | as C |
| D dimension value | `emotion.intensity` (value) | ICC(2,1), no judge |
| T / S free text | `narrative.harm`, `narrative.meaning`, `narrative.self_position`, `emotion.bodily_sensation`; `narrative.summary` | **Opus 5.5 judge equivalence, rules 1–5** |

Sub-members that are not the lead unit (`scope.direction`, `tether.referent` / `stake`, `intensity.text`) are extracted with their field and reported descriptively; they do not enter Q1–Q3.

**Prompt (one system prompt for all seven extractors).** The run-1 shared header (rules 1–4 verbatim, `experiments/2026-10-17/prompts/extraction_system.txt`) followed by a 19-field block generated at run time from `scripts/v09_layout.py` `DESC` and the draft fragments, in `LAYOUT_ORDER`, with the draft description, `x_constraints` and recommended values per field exactly as the draft schema states them (so `harm` carries its run-2 Arm B definition and referent rule, `meaning` its R6 text, `summary` the control text of runs 1–2). The block is compared at run time with `draft-schema/` and a mismatch aborts the run. The stated-only list in the header names `self_position`, `bodily_sensation`, `attribution`, `function`, `turning_point` (not `meaning`, R6). User message as runs 1–2.

**Limitation stated now.** The voters' majority answers come from a 47-field prompt (run 1) and a 7-field prompt (run 2, `harm`); run 3 uses a 19-field prompt. Run 2 showed framing can change what is extracted on some slots (cross-arm equivalence 0.36–0.79). A new model's disagreement with the majority therefore has two readings, vendor and framing. The Haiku reference arm bounds the framing effect for one model (its run-1 and run-3 answers are both available); a voter re-run under the 19-field prompt (Sonnet 5.5, ≈ USD 6) would bound it properly and is listed in §10 as the first extension if budget remains after the judge pass.

## 5. Judge (free-text fields only; one pass covers repeatability and agreement with the majority)

For each text and each free-text field the judge receives **all** run-3 answers for that field (6 arms + reference × 5 repeats = 35, indexed, arm hidden) **plus the three voters' representatives** from the run that classed the field (run 1 for `summary`, `meaning`, `self_position`, `bodily_sensation`; run 2 Arm B for `harm`; representative = the answer from the voter's largest within-model equivalence class in that run's judge grouping, re-read from `scoring/`), 38 answers in all, and groups them into equivalence classes under rules 1–5 (`experiments/2026-10-18-run2/prompts/judge_system.txt`, verbatim; rule 5: length is not a difference, judge the referent). Null answers form the "null" class. From one grouping the scorer reads, per arm: repeatability (fraction of its repeat pairs in the same class) and **majority agreement** (its representative falls in the class that holds ≥ 2 of the 3 voter representatives; a text where no two voters share a class is excluded for that field and the exclusion rate is reported).

Judge calls: per text, `summary` alone and the other four free-text fields together = **2 calls per text, 300 calls**, 38–152 answers each.

## 6. Scoring without a judge (coded, boolean, numeric)

Per arm and field, over the 150 texts, exactly as `experiment-plan.md` §4.2 with the voters' majority as the comparator:

- **Repeatability:** Fleiss κ over subjects = texts, raters = 5 repeats, categories = normalised labels (lower-cased, trimmed, deprecated values mapped per `DEPRECATED_VALUES`, null its own category); `intensity.value` ICC(2,1) over texts × repeats on texts where all five repeats give a number (coverage reported).
- **Majority label per text:** each voter's modal label over its five run-1 repeats (ties → earliest repeat, as run 1); the majority = the label ≥ 2 of 3 voters share; texts with no majority are excluded for that field (exclusion rate reported). For `intensity.value`: the voters' per-text mean over the voters that gave a number.
- **Majority agreement:** Cohen's κ between the arm's modal label and the majority label over the included texts; for `intensity.value`, ICC(2,1) between the arm's per-text mean and the voters' per-text mean over texts where both exist.
- Also reported: null rate per arm × field; non-canonical rate; cross-model κ among the six new arms (descriptive); invalid-output rate per arm; the `provider` field distribution per arm.

## 7. Decision rule (fixed now)

Thresholds verbatim from run 1 (`experiment-plan.md` §4.1): repeatability κ ≥ 0.70 (coded / boolean), judge-equivalence ≥ 0.80 (free text), ICC ≥ 0.75 (value); agreement κ ≥ 0.40 (coded / boolean), judge-equivalence ≥ 0.60 (free text), ICC ≥ 0.50 (value), here applied to **agreement with the majority** rather than to cross-model agreement among the arms. Borderline (within 0.05) and sparse (null ≥ 90 %) flags as in run 1; a field × arm cell with coverage below 50 % of texts (exclusions plus nulls) is reported as **uncovered** and counts as not held.

- **Per model × field:** the arm **holds** the field when both thresholds are met; **repeats only** when repeatability is met and agreement is not; **does not hold** otherwise. This is the model × field capability table.
- **Per field:** "comparable" **holds across the market** when ≥ 5 of the 9 models hold it, the three voters counting as holding by the run that classed the field (so the rule needs ≥ 2 of the 6 new arms). Reported beside it, descriptively and not deciding: the count among the six new arms alone.
- **Pre-registered recommendation if a field fails the 5-of-9 rule:** re-class it `interpretive` (repeatable within some extractors, not comparable across the market), which under R17 moves it from Essential to Extended. Recommendation only; the founder rules, veto by exception.
- **Reference arm:** Haiku 5.5 is scored identically and reported in the same table but is not one of the 9 and never changes a field verdict.

**Pre-registered predictions** (fixed with this draft; RESULTS.md reports each as held / not held; they do not alter the decision rule). Baseline figures from runs 1–2 on these 19 fields (lead units; repeatability met under the frozen thresholds): Sonnet 5.5 19 of 19, Kimi K2.6 19 of 19, gpt-6.1-sol 18 of 19 (misses `intensity.value`, which it leaves null 93 % of the time), **Haiku 5.5 11 of 19** (misses `harm` 0.78, `summary` 0.79, `scope` 0.69, `function` 0.68, `action_tendency` 0.66, `need` 0.68, `temporal_focus` 0.61, `coping` 0.69). Bands: **cheap-tier band** = repeatability met on ≤ 13 of 19; **voting band** = ≥ 17 of 19; 14–16 = between.

| # | Prediction | Reading if it holds |
|---|---|---|
| P1 (the founder's, pre-registered) | **The open-weight arms behave like the reported cheap tier:** each of N2 DeepSeek V4 Pro, N3 Qwen3.8 2.4T, N4 Llama 4 Maverick, N6 gpt-oss-120b (and N5 Mistral Large 4 if confirmed open-weight at freeze) lands in the cheap-tier band (repeatability met on ≤ 13 of 19) and holds (repeat + majority agreement) ≤ 10 of 19 | "comparable" is a property of the frontier closed tier; the Essential profile is a claim about that tier and the schema should say so |
| P2 | N1 Gemini 4 Argon lands in the voting band (≥ 17 of 19) and holds ≥ 15 | the class generalises across closed frontier vendors |
| P3 | The coded fields that passed run-1 cross κ at or just above 0.40 (`action_tendency` 0.40, `scope` 0.47, `need` 0.50) are the first to fail the 5-of-9 rule; `primary`, `valence`, `attribution`, `bodily_sensation`, `summary` hold across ≥ 8 of 9 | the borderline flag in `x_run1` predicts market fragility |
| P4 | `intensity.value` is left null on ≥ 50 % of texts by at least three of the six new arms (the gpt-6.1-sol pattern), so it fails on coverage rather than on agreement | R8's "per-extractor weight" reading extends to the market |

## 8. Null and coverage (descriptive)

Null rate per arm × field; for the stated-only fields with synthetic ground truth (`self_position`, `bodily_sensation`, `attribution`, `function`, `turning_point`) null-on-no and populated-on-yes per arm as `experiment-plan.md` §4.4; `meaning` reported by null rate only (R6). Coverage of `intensity.value` per arm (share of texts with five numbers).

## 9. Cost projection (list prices of §3; token assumptions stated; no caching assumed for the gateway arms)

Assumptions: input ≈ 3,600 tokens per call (a 19-field system block ≈ 3,000 against run-1's ≈ 6,600 for 47 fields, plus the text ≈ 600); visible output ≈ 600 tokens (19 of 47 fields; run-1 Sonnet produced 1,347 for 47); **upper bound** adds 3,000 reasoning tokens billed as output on every arm that exposes a reasoning parameter (all but Llama 4 Maverick). Per-call cost = (3,600 × in + out_tokens × out) / 10⁶.

| Call set | Calls | Projected USD | Upper bound (reasoning 3,000 tokens) |
|---|---|---|---|
| N1 `google/gemini-4-argon` (2.00 / 10.00) | 750 | 9.9 | 32.4 |
| N2 `deepseek/deepseek-v4-pro-0813` (0.66 / 1.98) | 750 | 2.7 | 7.1 |
| N3 `qwen/qwen3.8-2.4t-a95b` (2.00 / 6.00) | 750 | 8.1 | 21.6 |
| N4 `meta-llama/llama-4-maverick` (0.1875 / 0.6525) | 750 | 0.8 | 0.8 (no reasoning) |
| N5 `mistralai/mistral-large-4-0` (0.68 / 2.09) | 750 | 2.8 | 7.5 |
| N6 `openai/gpt-oss-120b` (0.15 / 0.60) | 750 | 0.7 | 2.0 |
| Ref `claude-haiku-5-5` (0.10 / 0.50; run-2 measured ≈ 0.0016 per 7-field call) | 750 | 1.2 | 2.4 |
| Pilot: 3 texts × 7 extractors × 1 repeat | 21 | 0.1 | 0.3 |
| Judge Opus 5.5: 300 calls, ≈ 4,000 in / 500 out | 300 | 7.8 | 9.0 |
| **Total** | **5,271 + 300** | **≈ 34** | ≈ 83 without any shrink |

**Budget: USD 40, hard stop.** Pilot gate: after the 21 pilot calls, project per arm = measured per-call cost × 750 and total = Σ arms + judge reserve 9; if total > 40 apply in order (pre-registered now): (1) on each arm whose measured per-call cost exceeds 1.5 × its projected line, set `reasoning: {effort: "low"}` (or, where only a token cap is supported, `max_tokens` 4,000) and log it as a deviation for that arm; (2) drop the costliest arm by projection (N1 first by these numbers); the 5-of-9 rule then reads 5-of-8, never relaxed; (3) do not start. Re-project after every 1,000 calls; the judge pass runs only if spent + 9 ≤ 40.

## 10. What this plan does not test, and optional extensions (not costed into §9)

- The 28 fields outside the comparable tier (interpretive, null-driven, extractor-bound stay as classed); non-English text; human–model agreement; the `trait` fields.
- **Voter re-run under the 19-field prompt** (Sonnet 5.5, 750 calls ≈ USD 6; or all three voters ≈ USD 14): bounds the framing effect of §4 properly. First extension if the pilot leaves room; otherwise a run of its own.
- A second hosting provider per open-weight model (quantisation sensitivity): ≈ the arm's cost again per provider.
- `gpt-5.4-mini` under the run-3 prompt as a second cheap-tier reference (≈ USD 2).

## 11. Analysis plan and deliverables

1. Run directory `experiments/<date>-run3/` with the layout of run 2: `models.json` (pins, prices, hosting provider per arm, budget 40), `prompts/` (generated block + check), `corpus/corpus_manifest.jsonl`, `raw/<arm>/<corpus_arm>.jsonl`, `scoring/`, `spend*.json`, `RESULTS.md`, `STATUS.md`.
2. `run_extraction.py` from run 2 with the `openrouter` provider kind, provider pinning and `provider` recording; pilot gate as §9.
3. Validate every output (19 keys; shape coercion; invalid repeats logged, never re-sampled).
4. Judge pass (§5), checkpointed to `raw/judge/`.
5. `score_run3.py`: §6 statistics, §7 table (model × field: holds / repeats only / does not hold / uncovered), per-field 5-of-9 verdict, predictions P1–P4 against the bands, reference arm beside.
6. `RESULTS.md`; `REPORT.md` §7.4; ruling drafts per field that fails 5-of-9 (recommendation: re-class interpretive under R17), for the founder.

## 12. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-10-18 (later) | Plan drafted: six OpenRouter arms pinned by exact ID with list prices from the live listing of 2026-10-18, Haiku 5.5 as the same-prompt cheap-tier reference, 19 comparable-tier fields, coded fields by κ without a judge, five free-text fields judged by Opus 5.5 with rule 5, majority-agreement scoring, 5-of-9 rule, predictions P1–P4 with bands from runs 1–2, hard stop USD 40, pilot gate; **not run, not frozen** | founder instruction 2026-10-18, step 3 |
