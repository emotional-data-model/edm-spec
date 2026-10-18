# STATUS — run 3 (2026-10-18), closed

**Nothing was pushed.** All work is in local commits on `discovery/ontology-crosswalk` of `edm-spec` plus docs-only commits in `deepadata-com` (`planning/STATE.md` + session handoffs). `schema/` and `examples/` untouched on every branch.

**Closed 2026-10-18 on the founder's instruction** ("Close run 3. No push."): judge resumed as far as the credit allowed, re-scored, rulings R18–R30 recorded (`docs/discovery/ontology-crosswalk-2026-10/rulings-2026-10-18.md`), R18–R28 applied to the v0.9 draft (Essential 18 / Extended 28 / Full 47), docs and state brought in line. One item of the close could not be finished: **the judge pass** (below).

## Gates

| Gate | Requirement | Result |
|---|---|---|
| Freeze before any call | commit `run 3 pre-registration frozen` before the first call | **Passed.** `974408e` (plan amended per the founder's run-3 instruction; Anthropic direct key found capped and the three Claude models pinned through OpenRouter at freeze). Scaffold `cc96aee`; first call (pilot) after both |
| Prompt check | committed prompt equals the draft-schema generation (`build_prompts.py --check`) | **Passed** before every run, including the close's dry runs |
| Corpus identity | every text's sha256 equals the manifest | **Passed** (150 / 150) |
| Pilot | 24 calls, projection against the stop | **Three passes, 51 calls, USD 0.77.** Lever 1 (effort low; token cap for Mistral) → 70.0; lever 2 → stop 60; lever 3 → DeepSeek dropped (13.32 vs Qwen 13.31) → 56.7 ≤ 60 |
| Hard stop (USD 60 in force; credit USD 50) | projection every 1,000 calls | **Passed** against the stop (final extraction 43.46); the credit ceiling bit during the judge pass |
| Extraction | 7 arms × 750 calls, checkpointed, provider recorded | **Passed.** 5,250 / 5,250 records; 0 provider mismatches; 147 OpenRouter 429 transport failures re-requested once (R3-D3); Mistral 89 unparsable (115 truncated) stay failed repeats; Qwen 3, gpt-oss 7 unparsable |
| Judge | 300 Opus 5.5 calls (2 per text) | **Incomplete: credit exhausted, twice.** 194 of 300 calls: the four-field group (`harm`, `meaning`, `self_position`, `bodily_sensation`) on **127 of 150** texts, `summary` on **69 of 150**; 0 malformed; USD 5.12. The resume at the close served 6 calls before OpenRouter refused every call (402) with USD 0.52 of the credit left (the gateway reserves a call's maximum cost). **104 calls remain (23 four-field, 81 summary; ≈ USD 2.7).** `judge.py` resumes from the checkpoints once credit is added; then `score.py`, `results_md.py`, and regenerate the draft (`v09_layout.py` `RUN3` from `field_table.json`) |
| Scoring | frozen thresholds, 5-of-8 rule, bands, P1–P4; reading (b) beside | **Done** (`scoring/field_table.{json,md}`, `RESULTS.md`) |
| Rulings | R18–R30 from the drafts | **Recorded** (ruling under delegation, veto by exception); R18–R28 **applied** to the draft; R29 / R30 **procedures ready, not executed** (credit) |

**Spend:** USD 49.35 of the 50 credit (extraction 43.46, pilot 0.77, judge 5.12); OpenRouter reports 49.48 used, 0.52 left. Stop in force 60 (lever 2). Zero Anthropic-direct spend (key capped until 2026-11-01).

## Headline (RESULTS.md §1–§3; rulings R18–R28)

Frozen rule (reading (a), literal coverage clause), 5-of-8: **10 of 19 hold** (`primary` 7, `valence` 8, `intensity` 7, `meaning` 5, `event_category` 7, `relationship` 7, `need` 7, `temporal_focus` 7; `scope` and `action_tendency` at the minimum 5). Under **R18 reading (b)** (a null-valued answer counts as covered; adopted prospectively, deviation R3-D4): **17 of 19 hold**; `tether` (type) fails genuinely at 4 of 8 (**R26 → interpretive → Extended**) and `summary` fails on judge coverage only (every arm ≥ 0.87 / ≥ 0.75 on the 69 judged texts; **R20: class per the completed judge**, comparable until then). `attribution`, `coping` (and `action_tendency` by the same rule) hold at the minimum on cells within 0.05 of a threshold and carry `at_minimum` / `borderline` in `x_comparability_basis`.

Bands (repeat met / 19; holds frozen / (b)): Gemini 4 Argon voting (19; 12 / 17), Llama 4 Maverick voting (19; 9 / 13), gpt-oss-120b voting (19; 6 / 14), Qwen3.8 2.4T between (15; 8 / 14), Mistral Large 4 cheap-tier (5; 2 / 4), Haiku 5.5 reference cheap-tier (13; 7 / 12), Sonnet 5.5 re-run voting (19; 10 / 18). **P1–P4 none held**; framing bound κ 0.65–0.97 coded, 0.75–0.99 free text.

**Applied to the draft** (commit `bf97e22`): `scripts/v09_layout.py` §3d `RUN3` + §3e; Essential 18 / Extended 28 / Full 47 (the profiles nest, so only Essential shrinks); audit 57 / 185 / 0; 7 / 7 valid (6 / 7 strict, therapy's trait opt-in as designed); the synthetic Essential example relocates seven fields as before (v0.8.3 Essential carries no `tether`).

## Founder actions now open

1. **Top up OpenRouter by ≈ USD 3** and run, from the repo root: `python -P experiments/2026-10-18-run3/scripts/judge.py` (104 calls) → `score.py` → `results_md.py` → regenerate the draft (`docs/discovery/ontology-crosswalk-2026-10/`: `python -I scripts/v09_layout.py --membership`, the regeneration order in its README). R20 (`summary`) closes mechanically; R19 / R21 / R23 / R24 cannot fall below 5 of 8 on the 23 unjudged texts.
2. **R29 Mistral probe** (≈ USD 0.3): `python -P experiments/2026-10-18-run3/scripts/probe_mistral.py`; ≥ 9 of 10 parse → re-run the arm (founder sets the stop), else report "reasoning-cap artefact, excluded from the 8". No field verdict changes either way.
3. **R30 DeepSeek V4 Pro extension** (≈ USD 3–6 under the USD 8 cap): `python -P experiments/2026-10-18-run3/scripts/run_extraction.py --extension`; then set `levers.json` `extension_plan_R30.executed` true and re-score (5-of-9). The free-text supplement (`judge.py --rejudge`, ≈ USD 7.7) is outside the cap: founder's call.
4. **Veto window** on R18–R30 (`rulings-2026-10-18.md`).
5. **Anthropic direct key** capped until 2026-11-01; **publish v0.8.4** (R1); **push** (`deepadata-com` docs commits; `edm-spec` branches) — founder-only.

## Files to read first

`experiments/2026-10-18-run3/RESULTS.md` → `docs/discovery/ontology-crosswalk-2026-10/rulings-2026-10-18.md` (addendum R18–R30) → `levers.json` (every deviation, R3-D4, the R29 / R30 plans) → `REPORT.md` §7.4 → `v0.9-proposal.md` §10.6.
