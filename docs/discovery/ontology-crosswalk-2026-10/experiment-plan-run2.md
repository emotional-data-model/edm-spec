# Run 2 — prompt test on the six core slots (PRE-REGISTRATION DRAFT, 2026-10-18; NOT RUN)

Discovery output, branch `discovery/ontology-crosswalk`. Written under rulings R2, R3, R8 and R9 of `rulings-2026-10-18.md` (*ruling under delegation, veto by exception*). **No extraction, judge or rater call has been made for this plan.** It is frozen by a commit titled `run 2 pre-registration frozen` only when the founder authorises the spend; until then it is a draft and may be edited. Run directory when authorised: `experiments/<run-date>/` with the same layout as `experiments/2026-10-17/`.

## 0. What run 2 is

Run 1 (`experiment-plan.md`, `experiments/2026-10-17/RESULTS.md`) tested the 47-field v0.9 draft under **one** 47-field extraction prompt. For the six core slots of v0.8.3 (`core.anchor`, `spark`, `wound`, `fuel`, `bridge`, `echo` → draft `narrative.subject`, `trigger`, `harm`, `drive`, `integration`, `salience.retrieval_cues`) the pooled outcome was five cut and one null-driven pass, with a pattern — repeatable in Sonnet 5.5 (0.80–0.88), not in the other extractors, cross-model 0.18–0.72 — that an under-specified definition produces as readily as an unreliable field. Under that prompt the v0.8.3 field names were not used, the slots sat among 47 fields with v0.9 rules, and `echo` became a merged list with a different description (R3; accuracy note there). **Run 1 cannot separate field reliability from prompt description quality.**

Run 2 is therefore a **prompt test, not a field test**: the same 150 texts, the same extractors and the same frozen thresholds, with the six slots (plus `summary` as a control) extracted under two prompts that differ only in the field block:

| Arm | Field text | Names | Shapes |
|---|---|---|---|
| **A** | v0.8.3 description, 1–5 word constraint and examples **verbatim** from the crosswalk record (`draft-crosswalk/v0.8.3_to_v0.9.0.json`, `field_map[].run2_arm_a`, audited verbatim against `schema/fragments/core.json` by `crosswalk-audit-2026-10-18.md`) | `anchor`, `spark`, `wound`, `fuel`, `bridge`, `echo`, `narrative` | single strings, as in v0.8.3 |
| **B** | question-framed definitions with a referent rule (§4, written for this run) | `subject`, `trigger`, `harm`, `drive`, `integration`, `retrieval_cues`, `summary` | v0.9: single strings; `retrieval_cues` a list |

What run 2 decides (§7): per slot, whether the v0.8.3 text, the v0.9 definition, both or neither yield a repeatable, model-independent answer. What it does not decide: profile membership (R2 holds until the result is read; the decision table in §7 is the pre-registered recommendation, the founder rules).

**Amended 2026-10-18 after the diagnostic on run-1 disagreements** (`experiments/2026-10-18-diagnostic/RESULTS.md`; 645 text × slot items where the four modal answers were not judge-equivalent, each classified by Opus 5.5 as (a) multiple valid referents 42 %, (b) extractor wrong 13 %, (c) granularity only 20 %, (d) null vs populated 24 %; judge calls only, USD 4.33). The diagnostic changes this plan in three places and nothing else: the Arm B field block (§4.3) now carries the selection, specificity and null rules the per-slot recommendations ask for; `retrieval_cues` in Arm B is capped at three ordered cues; and §7 records the pre-registered expectation per slot. Arm A, the corpus, the extractors, the thresholds and the voting rule are unchanged.

## 1. Questions

| # | Question | Decides |
|---|---|---|
| Q1 | Per slot and arm: repeatability within extractor and agreement across the three voting extractors (frozen thresholds) | whether the slot is extractable under that text |
| Q2 | Per slot: do Arm A and Arm B name the **same referent** on the same text (cross-arm equivalence)? | whether the v0.9 renaming / reframing changes what is extracted, or only how it is worded |
| Q3 | Control: does `summary` (identical text in both arms) behave the same in both arms? | whether any A / B difference is slot-specific or prompt-wide |
| Q4 | Reported arms: how far do the cheap-tier extractors (Haiku 5.5; OpenAI mini) sit from the voting modal answer? | cost-tier guidance, no vote |
| Q5 | Task (a), conversational, rebuilt: does salience weighting beat recency on LoCoMo evidence-session ground truth? (re-analysis of run-1 outputs; no new calls) | whether the run-1 conversational failure was the design (R8) or the signal |

## 2. Corpus (unchanged)

The 150 texts of run 1, byte-identical (`experiments/2026-10-17/corpus/corpus_manifest.jsonl`; sha256 per text): synthetic 50 (S01–S50; ground-truth spans), conversational 50 (LoCoMo conv-42 / conv-48 sessions 1–10, CC BY-NC 4.0, **referenced by path, never copied**; LongMemEval 3 × 10 sessions, MIT, referenced by path), Pepys 50 (public domain, committed). Mean length 324 words (synthetic 254, conversational 332, Pepys 388). The run-2 manifest is a copy of the run-1 manifest with the run date changed; any sha256 mismatch at run time aborts the run.

## 3. Extractors, judge, sampling (R9; same pins, no premium re-run)

| Slot | Model | Role | Price USD / M tokens (in / cached / out) | Note |
|---|---|---|---|---|
| M1 | `claude-sonnet-5-5` | **voting** | 2.00 / 0.20 / 10.00 (cache write 2.50) | provider defaults (adaptive thinking) |
| M3 | `gpt-6.1-sol` | **voting** | 2.00 / 0.10 / 10.00 | `gpt-6-astra` stays excluded (budget; R9) |
| M4 | `kimi-k2.6` | **voting** | 0.95 / 0.16 / 4.00 | `thinking: {type: disabled}` as in run 1 (D1); `kimi-k3` not chosen |
| M2 | `claude-haiku-5-5` | reported, cheap tier, **no vote** | 0.10 / 0.01 / 0.50 | run-1 repeatability 15 / 52 units |
| M5 | OpenAI current mini model: `gpt-5.4-mini` | reported, **no vote** | **to pin at run time** from developers.openai.com pricing; not in `models.json` | newest `*-mini` general model in the 2026-10-17 OpenAI listing (`experiments/2026-10-17/_model_lists_raw.json`: `gpt-5.4-mini`, created 2026-03-17; no `gpt-6*-mini` listed). Re-check the listing on the run date; if a newer mini exists, pin it and record both |
| Judge | `claude-opus-5-5` | equivalence judge | 4.00 / 0.20 / 20.00 | never an extractor; `output_config.effort = "low"` as in run 1 |

Voting rule (R9, stated openly): a slot **passes** in an arm when all three voting extractors meet the repeatability threshold and the cross-model threshold is met over the three; **interpretive** when all three meet repeatability and cross is missed; **cut** when ≥ 2 of the three miss repeatability (one voting extractor missing = borderline-cut, reported as such). The reported arms never change an outcome.

Caveat recorded from the diagnostic (not a change to R9): on the six slots the per-extractor wrong-rate over the 645 run-1 disagreement items, counting class (b) and the wrong side of class (d), was Sonnet 5.5 0.09, Haiku 5.5 0.12, `gpt-6.1-sol` 0.15, `kimi-k2.6` 0.22, with `gpt-6.1-sol` wrong on 44 of 137 `retrieval_cues` items because it returns an empty list. Two of the three voters carry most of the null-side errors; a cross-model miss in run 2 is therefore read together with the per-extractor null rate per arm (§8) before it is attributed to the text.

Sampling, checkpointing, failed repeats, transport errors, prompt caching: as run 1 (`experiment-plan.md` §3), with the Anthropic cache at the 5-minute TTL (D2). Repeats: **5 per text per extractor per arm**; fresh context per call; arm order per (text, extractor) alternated A/B/A/B… by text index parity so that neither arm is systematically first.

**Calls.** Extraction: 150 texts × 5 repeats × 2 arms × 5 extractors = **7,500** (voting 4,500; reported 3,000). Judge: §5. Task (a): none.

## 4. Prompts

### 4.1 Shared header (identical in both arms, verbatim)

~~~text
You are an extraction engine for the Emotional Data Model (EDM). Read ONE source text and fill the 7 fields below. Return ONLY a JSON object, no prose and no code fences.

Rules
1. INTERPRETATION ONLY, ATTRIBUTED. Every value must be an interpretation of what the text states, attributable to a passage in it. Do not infer traits, diagnoses, hidden motives or likely feelings. If the text does not state or unmistakably paraphrase something, the field is null (or [] for a list field).
2. Use the text's own words where it has them. Lower case except proper names.
3. If the text is a conversation, the subject is the person whose experience is being related (the User in a companion transcript; the speakers jointly in a dialogue; the client in a clinical note). Describe their stated experience, not the assistant's or clinician's.
4. Output object: one key per field name below, in the order given. Return every key even when null.

Fields (7)
~~~

### 4.2 Arm A field block — v0.8.3 text verbatim (from `field_map[].run2_arm_a` of the crosswalk record)

~~~text
- `anchor` -> string|null
    Central person, object, or theme of the experience
    Constraints: 1–5 words (e.g., "grandmother", "dad's toolbox", "childhood home")
- `spark` -> string|null
    What triggered or initiated the emotional response
    Constraints: 1–5 words (e.g., "finding old photos", "first snow", "phone call")
- `wound` -> string|null
    Emotional pain, loss, or vulnerability present in the experience
    Constraints: 1–5 words (e.g., "abandonment", "regret", "distance", "grief")
- `fuel` -> string|null
    What energized or motivated the experience
    Constraints: 1–5 words (e.g., "love", "shared laughter", "curiosity", "hope")
- `bridge` -> string|null
    Connection or shift between past and present understanding
    Constraints: 1–5 words (e.g., "forgiveness", "acceptance", "returning home")
- `echo` -> string|null
    What continues to resonate or recur from the experience
    Constraints: 1–5 words (e.g., "her laugh", "smell of rain", "city lights")
- `narrative` -> string|null
    A compressed, faithful account of the experience as described by the source, preserving emotional sequence, temporal markers, and stated context without interpretation
    Constraints: 3–5 sentences
~~~

The Arm A block is generated at run time from the crosswalk record and compared byte-for-byte with `schema/fragments/core.json`; a mismatch aborts the run.

### 4.3 Arm B field block — v0.9 names and shapes, question-framed definitions, referent rule

~~~text
Referent rule (applies to subject, trigger, harm, drive, integration, retrieval_cues): each answer names ONE referent that the text itself mentions — a person, object, place, event, feeling or idea — using the text's own noun phrase where it has one. If several candidates qualify, choose the one the text returns to most (mentioned most often, or dwelt on at the end). Use the most specific noun phrase the text itself uses that fits in 1–5 words; do not substitute a category the text does not use (write "the second sandwich", not "food") and do not add detail the text does not give. Null when no passage supports an answer; never null when one does.

- `subject` -> string|null
    Who or what is this experience about? Name the central person, object or theme the text keeps returning to.
- `trigger` -> string|null
    What set the feeling off? Name the moment, event or perception the text presents as starting the response it dwells on most. Not the topic of the text and not its subject; if the text states a feeling without an initiating event, null.
- `harm` -> string|null
    What hurt? Name the loss, pain or vulnerability the text states, in the text's own word where it has one. A stated worry, fear, loss or vulnerability counts; one you would have to infer does not. Null if the text states none.
- `drive` -> string|null
    What gave the experience its energy? Name the one thing the text says motivated, lifted or pushed the subject — a stated motive, hope, person or activity. Null if the text names none.
- `integration` -> string|null
    What links then and now? Name the connection or shift between past and present understanding that the text states: a comparison of then and now, a lesson the text states, a change of mind the text names. Null if the text draws none.
- `retrieval_cues` -> array of strings
    What would bring this back? List at most THREE cues the text says still resonate or would re-evoke the experience (a sensory detail, a phrase, an object), 1–5 words each, the first being the one the text returns to most. Empty list only if the text names nothing that recurs.
- `summary` -> string|null
    A compressed, faithful account of the experience as described by the source, preserving emotional sequence, temporal markers, and stated context without interpretation
    Constraints: 3–5 sentences
~~~

`summary` is the control: its text is identical in both arms (only the key name differs), so an A / B difference on it measures prompt-wide drift, not a slot effect.

Where each Arm B rule comes from (diagnostic, pooled shares of the slot's disagreement items): the selection clause from (a) multiple valid referents (`subject` 48 %, `trigger` 42 %, `harm` 37 %, `drive` 33 %); the specificity clause from (c) granularity (`subject` 28 %, `harm` 28 %, `drive` 23 %, `integration` 25 %); the `trigger` exclusion from its (b) share (28 %, the highest; extractors named the topic or a later episode); the null clauses from (d), where the text supported the populated answer in 129 of 157 items (extractors under-populate rather than invent); the `retrieval_cues` cap and ordering from its (a) share (53 %, with four or more valid cues in 65 of 73 such items) and the whole-list comparison of run 1.

### 4.4 User message (both arms, as run 1)

~~~text
Source text (id: {text_id}):

<text>
{text}
</text>

Return the JSON object now.
~~~

## 5. Judge (equivalence) — one pass covers within-arm, cross-model and cross-arm agreement

For each text and each slot pair, the judge receives **all** answers for that slot from both arms, all five extractors and all five repeats (2 × 5 × 5 = 50 answers, indexed; arm and extractor hidden) and groups them into equivalence classes. Null answers form the "null" class. From one grouping the scorer reads:

- repeatability per extractor per arm (fraction of that extractor's repeat pairs in the same class);
- cross-model agreement per arm over the three voting extractors (representatives = each extractor's largest within-arm class);
- **cross-arm equivalence** per extractor: whether the extractor's Arm A representative and Arm B representative fall in the same class (Q2);
- the same for the reported arms, descriptively.

Judge calls: per text, three slot-pair groups ({anchor / subject, spark / trigger}, {wound / harm, fuel / drive}, {bridge / integration, echo / retrieval_cues}) plus `narrative / summary` alone = **4 calls per text, 600 calls**, 50–100 answers each.

**Judge instruction added for run 2 (verbatim, appended to the run-1 judge system prompt as rule 5):**

~~~text
5. LENGTH IS NOT A DIFFERENCE. A 1–5 word answer and a clause-length paraphrase are EQUIVALENT when they name the same referent ("her laugh" = "the way she laughed at the table"; "the second sandwich" = "eating the sandwich while waiting"). A list answer is equivalent to a single answer when its first element, or any element, names that referent; two lists are equivalent when they share their first referent. Judge the referent, not the wording or the length.
~~~

The run-1 judge rules 1–4 are kept verbatim (`experiments/2026-10-17/prompts/judge_system.txt`).

## 6. Task (a), conversational arm, rebuilt on LoCoMo QA evidence sessions (R8; re-analysis, no new calls)

Run 1's conversational arm was uninformative by construction: LoCoMo probes are spread over sessions so any k-of-n policy scores ≈ k / n, both policies sat below the random floor, and LongMemEval hit rates move in steps of 0.5 over three blocks. Run 2 rebuilds the ground truth from the benchmark's own evidence citations and rescores the **run-1 checkpointed outputs** (`experiments/2026-10-17/raw/<model>/conversational.jsonl`), so no extraction is needed; the six-slot prompt of this run does not produce salience weights and is not used here.

- **Blocks:** the two LoCoMo conversations (sessions 1–10 each). LongMemEval is dropped from task (a) (its haystack is seeded distractors; retention of 2 answer sessions among 8 noise sessions does not test salience).
- **Named items ("what the later record names"):** per conversation, the **4 sessions most often cited as evidence** by the LoCoMo QA set over all probe categories (`task_a_blocks.json` `evidence.probes[].sessions`); ties broken by the count of single-session probes citing the session, then by the earlier session. Fixed now from the ground truth alone, before any model output is read for this question:

| Block | Citations per session 1…10 | Named (top 4) | Recency keeps (sessions 8–10) | Recency hit rate |
|---|---|---|---|---|
| conv-42 | 12, 21, 13, 8, 8, 4, 9, 5, 12, 16 | L42-02, L42-10, L42-03, L42-09 (tie 12 / 12 with L42-01 broken by single-session citations 11 vs 6) | L42-08, L42-09, L42-10 | 0.50 |
| conv-48 | 12, 26, 9, 16, 7, 12, 8, 6, 2, 8 | L48-02, L48-04, L48-01, L48-06 | L48-08, L48-09, L48-10 | 0.00 |

Recency mean 0.25; random floor (3 of 10 with 4 named) 0.30. The ground truth is informative: a salience policy has to reach a mean hit rate ≥ 0.35 to pass.

- **Policies (R8):** `S = mean(emotion.intensity.value, salience.linkage_strength)` (medians over repeats; a missing component dropped; no component → ranked last), k = 3; `S_intensity` and `S_linkage` alone reported; persistence is no longer a component. Run once per extractor (all four run-1 extractors, since the outputs exist; the voting three decide).
- **Pass (same verbatim rule as run 1):** mean over the two blocks of (salience − recency) ≥ 0.10 for ≥ 2 of the 3 voting extractors. **Caveat stated now:** two blocks of ten give a coarse statistic (steps of 0.125 in the mean); the result is reported with both block values and is a finding about these two conversations. Extending to the other eight LoCoMo conversations would need 80 new session extractions carrying the salience weights (≈ 80 × 4 extractors × 5 repeats = 1,600 calls under a weights-only prompt) and is **not** part of this plan; it is listed in §10 as an optional extension with its own cost line.

## 7. Decision rule (fixed now)

Thresholds verbatim from run 1 (`experiment-plan.md` §4.1): free text judge-equivalence ≥ 0.80 repeatability, ≥ 0.60 cross-model; `retrieval_cues` scored as a list (L shape: the whole list is one answer, with judge rule 5); `summary` as S. Borderline (within 0.05) and sparse (null ≥ 90 %) flags as in run 1.

Per slot, with outcomes under Arm A and Arm B over the three voting extractors:

| Arm A | Arm B | Reading | Pre-registered recommendation to the founder |
|---|---|---|---|
| pass | pass | the slot is reliable under either text | keep in Essential; adopt the v0.9 name; use the Arm B definition if cross-arm equivalence ≥ 0.60 for all three voting extractors (same referent either way), else keep the v0.8.3 wording under the v0.9 name |
| pass | interpretive / cut | the v0.9 definition is at fault | keep in Essential with the v0.8.3 wording and, for `echo`, the single-string shape; the question-framed text is withdrawn for that slot |
| interpretive / cut | pass | the v0.8.3 text is at fault | keep in Essential with the Arm B definition and shape |
| interpretive | interpretive | model-dependent under both | keep as text, `x_comparability: "interpretive"`; no cross-system comparison claim |
| cut | cut | the field itself does not replicate under either text | **founder decision**; pre-registered recommendation: move the slot out of Essential (to Extended or to `extensions`), text preserved by migration |

Gate on the control: if `summary` differs between arms by ≥ 0.10 on cross-model agreement, the whole A / B comparison is reported as prompt-wide drift and the table above is advisory only (the per-arm outcomes still stand on their own).

Pre-registered expectations per slot, from the diagnostic (`experiments/2026-10-18-diagnostic/RESULTS.md` §4). They are stated so that the result can be read against them; they do not alter the decision table:

| Slot | Expectation under Arm B | Recommended shape if the expectation holds |
|---|---|---|
| `subject` | pass (disagreement was selection and specificity, extractor error 13 %) | single string, selection rule |
| `trigger` | pass or interpretive (extractor error 28 %, the definition was misread) | single string, selection rule + exclusion |
| `harm` | pass; null rate falls (under-population in 17 of 25 (d) items) | single string, null threshold |
| `drive` | **interpretive** (non-error classes 83 %, mixed) | keep `x_comparability: "interpretive"`; no cross-system claim |
| `integration` | pass; null rate falls | single string, null rule |
| `retrieval_cues` | Arm B (capped list, first-element rule) passes where the run-1 list did not; Arm A `echo` single string is the comparison | short ordered list, cap 3 |

A result that contradicts an expectation is reported as such; the §7 table decides.

Reported arms (Haiku 5.5, `gpt-5.4-mini`): repeatability, agreement with the voting modal class, and cross-arm equivalence, all descriptive; a sentence per arm in RESULTS.md.

## 8. Null precision (synthetic arm; descriptive, as run 1 §4.4)

The synthetic design matrix has no ground-truth flags for the six slots, so null precision is not computed for them (confirmed by the diagnostic: no authored value exists for any of the six). `harm` and `integration` are expected to be null on a share of texts (run 1: 36 % and 67 % pooled); their null rate per arm is reported, and a slot whose null rate differs between arms by ≥ 0.20 is flagged (the two definitions are asking different questions). Per extractor and arm, the null rate is also reported (the diagnostic found the null side wrong in 129 of 157 null-vs-populated items, concentrated in `kimi-k2.6` and, for `retrieval_cues`, `gpt-6.1-sol`), so that a cross-model miss driven by one extractor's empty answers is visible as such.

## 9. Cost projection (scaled from `experiments/2026-10-17/spend.json`, list prices in `models.json`)

Measured run-1 per-call usage (extraction, 47 fields): Sonnet 5.5 in 618 / cached 6,588 / out 1,347 tokens = USD 0.0160; Haiku 5.5 618 / 6,588 / 2,894 = 0.0016; gpt-6.1-sol 87 / 4,569 / 1,382 = 0.0145; Kimi K2.6 595 / 4,085 / 965 = 0.0051. Judge (Opus 5.5) 2,480 in / 344 out = 0.0168 per call.

Scaling assumptions for a 7-field prompt: cached / system tokens × 0.22 (≈ 1,000-token system prompt against ≈ 4,600); uncached input unchanged (same texts); **output × 0.35** (7 of 47 fields, but Claude thinking tokens are not expected to shrink in proportion — this is the assumption the pilot checks). Mini priced at **one fifth of gpt-6.1-sol per token** as a placeholder (0.40 / 0.02 / 2.00) until pinned.

| Call set | Calls | Projected USD | Upper bound (run-1 per-call cost, no shrink) |
|---|---|---|---|
| M1 Sonnet 5.5 (A + B) | 1,500 | 9.4 | 24.0 |
| M3 gpt-6.1-sol | 1,500 | 7.7 | 21.7 |
| M4 Kimi K2.6 | 1,500 | 3.1 | 7.6 |
| M2 Haiku 5.5 (reported) | 1,500 | 0.9 | 2.4 |
| M5 gpt-5.4-mini (reported; price unpinned) | 1,500 | 1.5 | ≤ 21.7 (if it cost as much as sol) |
| Pilot: 3 texts × 5 extractors × 2 arms | 30 | 0.5 | 1.0 |
| Judge Opus 5.5: 600 calls, ≈ 3,000 in / 600 out | 600 | 14.4 | 18 |
| Task (a) re-analysis | 0 | 0 | 0 |
| **Total** | **7,530 + 600** | **≈ 38** | ≈ 97 without any shrink |

**Budget: USD 60, hard stop.** Pilot gate (as run 1): after the 30 pilot calls, project total = measured per-call cost × remaining calls + judge reserve 18; if > 60, apply in order (pre-registered now): (1) drop the `gpt-5.4-mini` arm; (2) run the two Claude extractors with `output_config.effort = "low"` (the only cost lever that does not alter sampling; logged as a deviation); (3) do not start. Re-project after every 1,000 calls.

## 10. What this plan does not test, and optional extensions (not costed into §9)

- The other 41 v0.9 fields; human–model agreement; non-English text; the `trait` fields.
- A run-1 → run-2 comparison for the five renamed slots (same texts, 47-field prompt vs 7-field prompt) would need run-1 answers added to the judge groups (+ ≈ 20 answers per slot per text, ≈ +40 % judge input): optional, USD ≈ 6, decide at freeze.
- Task (a) on all ten LoCoMo conversations: 80 new sessions × 4 extractors × 5 repeats under a weights-only prompt (`intensity.value`, `linkage_strength`), ≈ 1,600 calls ≈ USD 12 at run-1 rates scaled; optional.
- Tightening the stated-only wording of `self_position` (null leak 7–37 % in run 1): a later run; out of scope here (R7 keeps the field as drafted).

## 11. Analysis plan and deliverables

1. Validate every output: JSON object with the 7 keys; shape coercion (Arm B `retrieval_cues` list); invalid repeats logged, never re-sampled.
2. Judge pass (§5), checkpointed to `raw/judge/*.jsonl`.
3. Statistics per slot × arm × extractor (`scripts/score_run2.py`, adapted from `experiments/2026-10-17/scripts/score.py` and `stats.py`): repeatability, cross-model (voting three), cross-arm equivalence; flags; §7 decision table filled; control gate.
4. Task (a) re-analysis (`scripts/task_a_locomo.py`, adapted from `task_a.py`): the §6 table, per block and per extractor, components separately.
5. `RESULTS.md`: per-slot table per arm; cross-arm equivalence; control; reported arms; task (a); spend from per-call usage; every deviation. `REPORT.md` §7.2; `rulings` follow-up for the founder (profile membership, R2).

## 12. Change log

| Date | Change | Reason |
|---|---|---|
| 2026-10-18 | Plan written as a prompt test under R2 / R3 / R8 / R9; Arm A from the audited crosswalk record; Arm B definitions and referent rule written; judge rule 5; LoCoMo evidence-session ground truth fixed from citation counts; cost scaled from `spend.json`; **not run, not frozen** | founder instruction 2026-10-18 step 5 |
| 2026-10-18 (later) | Arm B referent rule gains a specificity clause; `trigger` gains the topic / subject exclusion and a null clause; `harm`, `drive`, `integration` gain null rules; `retrieval_cues` capped at three ordered cues; §3 caveat on per-extractor wrong-rates; §7 pre-registered expectations per slot; §8 per-extractor null rate. Arm A, corpus, extractors, thresholds, voting rule, cost unchanged; **still not run, not frozen** | diagnostic on run-1 disagreements, `experiments/2026-10-18-diagnostic/RESULTS.md` (founder instruction 2026-10-18, diagnostic) |
