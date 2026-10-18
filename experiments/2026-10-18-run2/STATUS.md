# STATUS — run 2 (2026-10-18)

**Nothing was pushed.** All work is in local commits on `discovery/ontology-crosswalk` of `edm-spec` plus a docs-only commit in `deepadata-com` (`planning/STATE.md` + session handoff). `schema/` and `examples/` untouched on every branch.

## Gates

| Gate | Requirement | Result |
|---|---|---|
| Freeze before any call | commit `run 2 pre-registration frozen` exists before the first extraction call | **Passed.** `b1354ee` (plan §3 pinned `gpt-5.4-mini` 0.75 / 0.075 / 4.50, §9 re-projected ≈ USD 39, §7 predictions). Scaffold `6f3cd82`; first call (pilot) after both |
| Arm A verbatim | Arm A block generated from the crosswalk record equals `schema/fragments/core.json` and plan §4.2 byte for byte | **Passed** (`scripts/build_prompts.py`) |
| Corpus identity | every text's sha256 equals the manifest | **Passed** (150 / 150; `load_texts`) |
| Pilot | 30 calls (3 texts × 5 extractors × 2 arms, plan §9); parsing and projection | **Passed.** USD 0.11; 1 of 30 malformed (Sonnet, two objects) → parser deviation R2-D1 before the main run; projection USD 27 + 18 reserve < 60 |
| Hard stop USD 60 | projection every 1,000 calls | **Passed.** Projection 38.2–38.5 throughout; actual extraction USD 20.16 |
| Extraction | 7,500 checkpointed calls | **Passed.** 7,500 / 7,500; 15 malformed outputs logged as failed repeats (0.2 %); 0 transport failures; 0 missing keys |
| Judge | 600 Opus 5.5 calls with rule 5 | **Passed.** 600 / 600, 0 malformed, USD 13.15 |
| Control gate | `summary` cross-model difference between arms < 0.10 | **Passed** (0.96 vs 0.98) |
| Scoring | frozen thresholds, three-voter rule; two-voter sensitivity beside it | **Done** (`scoring/field_table.{json,md}`, `RESULTS.md`) |
| Task (a) re-analysis | LoCoMo evidence sessions, run-1 outputs, no calls | **Done; passes** for all three voters under all policies |

**Spend:** USD 33.42 of 60 (extraction 20.16, judge 13.15, pilot 0.11). Diagnostic earlier the same day: USD 4.33 (separate cap of 8).

## Headline (RESULTS.md §1)

| Slot | Arm A (v0.8.3 text) | Arm B (v0.9 rules) | prediction |
|---|---|---|---|
| `harm` | borderline-cut (Kimi 0.79; two-voter pass) | **pass** | held |
| `trigger` | borderline-cut (Kimi 0.74) | **interpretive** | held |
| `subject` | borderline-cut | borderline-cut (B worse) | not held |
| `integration` | borderline-cut (Kimi 0.75; two-voter pass) | borderline-cut (GPT 0.79) | not held |
| `drive` | borderline-cut | cut | not held |
| `retrieval_cues` | borderline-cut | cut | not held |
| `summary` (control) | pass | pass | — |

## Founder decisions now open

1. **Rulings R11–R16 recorded** (`docs/discovery/ontology-crosswalk-2026-10/rulings-2026-10-18.md`, from the drafts in RESULTS.md §7, ruling under delegation, veto by exception): R11 `harm` Arm B, Essential; R12 `trigger` Arm B, Essential, interpretive; R13 `subject` Arm A, interpretive, **membership founder-only** (stays in Essential until ruled; pre-registered recommendation is to move); R14 `integration` Arm A, Essential (a stated departure from the pre-registered move); R15 `drive` and R16 `retrieval_cues` to Extended (pre-registered). Veto window open; nothing applied to the draft layout yet.
2. **Voting rule for run 3** (R9): Kimi K2.6 is the voter below 0.80 in 8 of 12 cells; the two-voter sensitivity changes only `harm` A and `integration` A.
3. **Publish v0.8.4** (R1, still open) and **push** (`deepadata-com` `6a1f597`, `536db0f`, this session's commit; `edm-spec` branches) — founder-only.
4. **Run-2 → v0.9 draft**: apply R11–R16 to `v09_layout.py` (`ESSENTIAL_09`, `DESC`) / `draft_schema_build.py` / crosswalk record / `v0.9-proposal.md` after the veto window and the R13 membership decision (nothing applied in this session).

## Files to read first

`experiments/2026-10-18-run2/RESULTS.md` → `docs/discovery/ontology-crosswalk-2026-10/experiment-plan-run2.md` §7 / §12 → `experiments/2026-10-18-diagnostic/RESULTS.md` → `REPORT.md` §7.2.
