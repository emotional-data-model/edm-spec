# Pre-registration — run 4, spans, cues and reconciliation (2026-10-18)

**Status: pre-registered, NOT frozen, NOT run.** No call has been made under this plan. It becomes binding only with a commit `run 4 pre-registration frozen` after the founder's review of the open items in §11; the private arm (§9) is deferred until Anthropic direct access is restored (the key's console cap lifts 2026-11-01) and is never run through a gateway.

## 1. Questions

Runs 1–3 scored *values*. Run 4 scores *where the values come from* and *what licenses them*, using the additive `reading` block of `schema-sketch.md` and the cue catalogue `cues-v1.md`.

- **Q1 (spans).** When three extractors populate the same field on the same text, do they point at the same place? Per field: character-span overlap between extractors (and within an extractor across repeats).
- **Q2 (cues).** Do three extractors see the same cues in the same text? Per cue code: agreement on presence, and on presence at the same span.
- **Q3 (cue → label stability).** Given a cue, do the three extractors license the same field and label from it? And how often does an extractor license *content* (`emotion.primary`, `narrative.harm`, `narrative.trigger`) from a cue the catalogue marks process-only (the over-reading rate)?
- **Q4 (reconciliation).** On the interpretive tier, does one revision pass in which each extractor sees the other two extractors' modal answers *with their spans* raise cross-model agreement, and does it do so without the revised values losing their evidence?

## 2. Corpus

**50 of the 150 public texts of runs 1–3** (synthetic 17, conversational 17, Pepys 16), drawn by `scripts/sample_run4.py` from `experiments/2026-10-18-run3/corpus/corpus_manifest.jsonl` (ids and sha256 only; LoCoMo texts are resolved at run time from the run-1 cache, never committed), stratified by corpus arm, seed 20261019. The sampler is written and tested (it prints the 50 ids); the id list is written into this file at the freeze. Texts are byte-identical to runs 1–3 (sha256-checked at load).

The founder's archive is **not** part of this run; see §9.

## 3. Extractors

Three voters, three repeats each, fresh context per call:

| Tag | Model | Route | Why |
|---|---|---|---|
| S | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | Anthropic direct if restored, else OpenRouter `anthropic` endpoint as run 3 | voting band in every run; the framing-bound model |
| G | Gemini 4 Argon (`google/gemini-4-argon` @ `google-vertex/global`) | OpenRouter, run-3 pin | voting band in run 3 (repeat met 19 / 19, holds 14 of 19) |
| O | gpt-6.1-sol | OpenAI direct (run-1 pin) | run-1 / run-2 voter; the majority construct of runs 1–3 |

No reference arm, no cheap-tier arm. Judge: Claude Opus 5.5 (rule 5 of the run-2 judge prompt) only for the three free-text interpretive fields in §7 (Q4), ≈ 100 calls.

## 4. Fields and prompt

**Fields:** the 28 of the Extended profile (comparable 18 + interpretive 8 + null-driven 2; `draft-schema/edm.v0.9.extended.schema.json` at the freeze commit), under their draft descriptions and constraints, generated as in run 3 (`build_prompts.py` pattern: header + field block cross-checked against `v09_layout.DESC`). **Plus the reading block:** for every populated field, `evidence` spans per `schema-sketch.md` §3 (stated fields exactly one span; interpreted fields one to three); and `readings`, zero or more, each with cue code(s) from the catalogue, span(s), field, licensed label, licence and norm.

**Prompt additions over run 3:** (i) the evidence rule (§3 of the sketch) verbatim; (ii) the 35 cue codes with their one-line definitions and their process / content column from `cues-v1.md` §8, and rule 2 of §9 ("process is not content") verbatim; (iii) the offset convention: character offsets into the text exactly as given between the `<text>` tags, NFC, LF, 0-based, end exclusive, with the quote repeated so that offset arithmetic can be checked and corrected by the scorer. Output: one JSON object with the 28 field keys, then `reading` as in the fragment.

**Offset repair (frozen rule):** models miscount offsets. The scorer accepts a span when `quote` is found in the text; if the stated offsets do not match the quote, the scorer re-locates the quote (first exact occurrence after the previous span's end, else first occurrence anywhere) and records `offset_corrected: true`. A quote not found verbatim (after whitespace normalisation) is a **missing span** for that field and extractor. Correction rates are reported per model; they are a finding, not a failure.

## 5. Measures (frozen)

Let `E(m, r, t, f)` be the set of character positions covered by extractor *m*'s evidence spans for field *f* on text *t* in repeat *r* (union of its spans), empty when the field is null or has no accepted span.

- **M1 Span overlap per field (Q1).** For each (t, f) populated with ≥ 1 accepted span by ≥ 2 extractors, the mean pairwise **Jaccard** of `E` over extractor pairs, using each extractor's repeat-1 spans (and, as a sensitivity, the repeat whose spans are the median by length). Reported per field as the mean over texts, with the share of texts populated by ≥ 2 extractors. **Within-model span repeatability:** mean pairwise Jaccard over an extractor's three repeats, per field. Thresholds (pre-registered, from no prior data): **stated fields ≥ 0.50**, **interpreted comparable fields ≥ 0.30**, **interpretive tier ≥ 0.30**; a field below its threshold is "reads from different places".
- **M2 Cue agreement κ (Q2).** Per (t, cue code): each extractor 1 / 0 for "recorded this cue anywhere in t" (repeat 1); **Fleiss' κ** over the three extractors pooled across texts, per cue and per family (§1–§7 of the catalogue), with prevalence beside (a cue recorded by no one on most texts has an undefined or unstable κ: reported, not scored, when prevalence < 5 %). **Span-matched variant:** the cue counts as shared between two extractors only when their spans for it overlap with Jaccard ≥ 0.50.
- **M3 Cue → label stability (Q3).** For each cue code with ≥ 10 readings from each extractor: the extractor's **modal (field, licence)** pair and, among readings with a non-null `label_licensed`, the modal label. **Stable** when all three extractors share the modal field and (where labels exist) the modal label. **Over-reading rate** per extractor: share of readings with `field` ∈ {`emotion.primary`, `narrative.harm`, `narrative.trigger`} and `licence` ≠ `pointer` whose cue is marked process-only in the catalogue (every cue except `rl:unasked-denial`, `rl:unfinished`, `rl:self-repair`, `rl:counterfactual`, `rl:minimising`, `rl:late-return`, `rl:over-explaining`, `rl:tense-shift-person`, `rl:pronoun-distance`, which the catalogue lists as content candidates or hypotheses).
- **M4 Reconciliation (Q4).** On the interpretive tier — `narrative.subject`, `narrative.trigger`, `narrative.drive`, `salience.tether` (type), `emotion.temporal_profile`, `salience.memory_type`, `salience.linkage_strength`, `motivation.risk_posture` — compute cross-model agreement before and after the revision pass (§7): Fleiss' κ across the three extractors' modal answers for the coded units; judge same-class rate (Opus, rule 5) for the three free-text fields (`subject`, `trigger`, `drive`); ICC(2,1) for `linkage_strength`. **Evidence retention:** for each revised value, whether its new evidence spans are accepted (§4 rule) and the Jaccard of the new spans against the extractor's own pre-revision spans. A revision that adopts another extractor's value must carry a span; a revised value with no accepted span is scored as null.
- **Descriptives:** per model offset-correction rate, spans per populated field, readings per text, cue prevalence, licence distribution (pointer / hypothesis / candidate), `populated` rate (how often a reading's label became the field's value), flags.

## 6. Predictions (frozen before the run)

- **P1.** Stated fields reach the span threshold: mean pairwise Jaccard ≥ 0.50 on ≥ 4 of the 5 stated fields (`self_position`, `bodily_sensation`, `appraisal.attribution`, `turning_point`, `function`).
- **P2.** The interpretive tier reads from different places: mean pairwise Jaccard < 0.30 on ≥ 5 of its 8 fields, with within-model span repeatability above cross-model overlap on every one of the 8 (each extractor is consistent with itself about where it reads; they differ from each other).
- **P3.** Cue agreement is a family property: Fleiss' κ ≥ 0.40 for the timing and repetition families, < 0.40 for the manner and person families (manner cues are the easiest to see everywhere and the hardest to agree on).
- **P4.** Every extractor over-reads: over-reading rate > 10 % for each of S, G, O; S lowest.
- **P5.** Reconciliation raises interpretive-tier agreement by ≥ 0.10 (κ or same-class rate) on ≥ 5 of 8 fields, and the revised values retain evidence: ≥ 80 % of revised values carry an accepted span, and the median Jaccard of new against old spans is ≥ 0.30 (the revision moves the value, not the reading).
- **P6.** Cue → label stability holds for ≤ half of the cues with enough readings (the catalogue's "typical licence" is not what the models do unprompted).

## 7. Reconciliation arm (procedure)

After the three repeats, for each extractor *m* and each text *t*: one further call with the text, *m*'s own modal values for the 8 interpretive fields with their evidence spans, and the other two extractors' modal values with *their* evidence spans, all three labelled A / B / C in a per-text random order with the models hidden. Instruction: *you may revise each of your eight values once; a revised value must be attributable to a span you cite; do not revise a value only because the others agree; record for each field whether you kept, revised or nulled it and why in one clause.* Output: the eight fields, their evidence, and a `reconciliation` object {field: kept | revised | nulled, reason}. Three repeats of the extraction, **one** reconciliation call per (m, t): 150 calls. The judge then classes the free-text interpretive answers before and after in one pass per text (≈ 50 calls of the run-2 judge pattern with both sets indexed and models hidden, plus ≈ 50 for `trigger` / `drive` if the groups do not fit one call).

## 8. Cost and stop

450 extraction calls (≈ 7,000 prompt tokens with the cue catalogue; ≈ 1,500 output), 150 reconciliation calls (≈ 9,000 / 1,500), ≈ 100 judge calls. Projection: S ≈ USD 6 (prompt cached on the direct API; ≈ 9 through the gateway with mandatory reasoning), G ≈ USD 6, O ≈ USD 5 (at the run-1 pin price), reconciliation ≈ USD 7, judge ≈ USD 2.5: **≈ USD 24–28 against a hard stop of USD 30.** Pilot: one text per arm per extractor (9 calls) → projection; levers in order: (1) `reasoning: effort low` on any arm whose measured cost exceeds 1.5 × the line; (2) repeats 3 → 2; (3) drop the reconciliation judge for `drive` (keep `subject`, `trigger`); (4) stop. Checkpointed per call; a re-run skips completed jobs.

## 9. Private arm — the founder's archive (protocol; deferred, not run)

**Why a private arm.** Every public text has been read by models in training or, in the companion arm, partly written by one; the cues in them may be the models' own. The founder's archive is the only corpus here that no model touched. It is also the only one whose cues are the writer's, which is the point of a reading layer.

**Conditions (all must hold before any call):** (a) Anthropic direct API access restored (the key's cap lifts 2026-11-01), with the organisation's zero-data-retention terms confirmed in writing by the founder; (b) **no gateway**: the private arm runs only against the Anthropic API directly, single vendor, so the three-voter design of §3 does not apply — the private measures are within-model span repeatability (Sonnet 5.5, three repeats) and cross-model overlap between Sonnet 5.5 and Claude Opus 5.5 as a second reader, the same M1–M3 statistics with two extractors; (c) the sampled texts never enter `edm-spec`, any experiment folder, any commit or any handoff; only the manifest (§9.1) and the aggregate statistics do; (d) the founder runs the sampler and the extraction themselves or is present; (e) the founder may withdraw any text before or after the run and the statistics are recomputed without it.

**9.1 Sampling script (written, not run): `scripts/sample_private.py`.** Takes the archive root as an argument (any tree of `.txt`, `.md` or `.json` files with a text field), reads each file only to compute its sha256, code-point length and a year (from YAML front matter `date:`, a leading ISO date in the file name, or the file's modification time, in that order), stratifies by year and by length tercile, draws 50 with a seed the founder supplies, and writes a manifest (`id` = sha256 prefix, relative path, sha256, length, year, tercile) to a path **outside** the repository that the founder names. It never prints, copies or stores text. Dry-run mode lists the strata counts only. The script lives in the repo; its output does not.

**9.2 What the private arm reports.** The same M1–M3 tables for two extractors, the cue prevalence per family against the public arms, and one sentence per family: *cue prevalence in the private arm is higher / lower / comparable to the public arms* — the first evidence of whether the catalogue's cues are the models' or the writer's.

## 10. Files (at freeze)

`experiments/<date>-run4/`: `corpus/sample_ids.json` (50 ids + sha256), `prompts/` (generated, `--check`-able against the draft at the freeze commit), `models.json` (pins), `scripts/` (`build_prompts.py`, `run_extraction.py`, `reconcile.py`, `judge.py`, `score.py`, `results_md.py` — to be written from the run-3 scripts), `levers.json`, `spend*.json`, `raw/`, `scoring/`, `RESULTS.md`, `STATUS.md`. `docs/discovery/reading-layer-2026-10/scripts/sample_run4.py` and `sample_private.py` (this folder).

## 11. Open before the freeze (founder)

1. Admit `reading` to the draft composites for the run's outputs to validate, or score the block as a sidecar (the sketch's open question 1).
2. Confirm the three voters (§3) and whether S runs direct or through the gateway (changes the cost line and the reasoning regime).
3. Confirm the Extended 28 as the field set, or restrict to the interpretive tier + stated fields (reduces the prompt and the cost by about a third; loses Q1 on the comparable tier).
4. The M1 thresholds (0.50 / 0.30) are set without prior data; accept them as frozen or replace them.
5. Private arm: the conditions in §9 and the seed.
