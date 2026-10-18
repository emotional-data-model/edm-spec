# STATUS — run 3 (2026-10-18), finished under Phase A of the overnight instruction

**Nothing was pushed.** All work is in local commits on `discovery/ontology-crosswalk` of `edm-spec` plus docs-only commits in `deepadata-com` (`planning/STATE.md` + session handoffs). `schema/` and `examples/` untouched on every branch. The founder's archive was not used.

**Phase A (2026-10-18 night, delegated; "finish run 3, cap USD 15"): done.** Judge completed, R20 closed, R29 probe run, R30 extension and its free-text supplement run, nine-model scoring, draft rebuilt, docs in line. One item is deferred to the founder: the **Mistral re-run** that the R29 probe authorised (over the cap).

## Phase A ledger (OpenRouter billed cost; cap USD 15)

| Step | Calls | USD |
|---|---|---|
| 1. Judge completion (104 + 7 rate-limited summary texts) | 111 | 3.22 |
| 2. R29 Mistral probe | 10 | 0.25 |
| 3a. R30 DeepSeek V4 Pro extension (reasoning off) | 750 | 1.27 |
| 3b. R30 free-text supplement (`--rejudge` 300 + `--rejudge-missing` 13) | 313 | 9.35 |
| **Total** | 1,184 | **14.09** |

Run-3 total since the freeze: USD 63.44 (extraction 43.46, pilot 0.77, judge 17.69, extension 1.27, probe 0.25) against the stop in force USD 72 (lever 4, twice amended so that the judge's 9-reserve start rule did not refuse the last calls; the Phase A cap was the binding limit). OpenRouter credit: 100 total, ≈ 65 used after Phase A and the Phase B pilot.

## Gates

| Gate | Result |
|---|---|
| Freeze before any call | **Passed** (`974408e`; unchanged) |
| Prompt check | **Passed** on every invocation after R3-D5 (the frozen 19-field list is now pinned in `build_prompts.py`; the live draft tier has 18 since R26) |
| Corpus identity | **Passed** (150 / 150 sha256) |
| Judge | **Complete**: both groups on 150 of 150 texts, eight arms (`scoring/8arm/`, `RESULTS.8arm.md`), then re-judged with all nine arms' answers (the latest record per text supersedes); 0 malformed in 912 judge records; 15 texts needed a second supplement call after OpenRouter 429s |
| R29 probe | **10 of 10 parsed** at max_tokens 32,000 / reasoning budget 8,000 (budget not honoured: mean 10,300 reasoning tokens; every call finished `stop`; USD 0.0247 per call) → branch 1 **"re-run the arm"**. The re-run (750 calls ≈ USD 18.5) exceeds the Phase A cap and is **deferred to the founder** (R29: the founder sets the stop). Mistral's run-3 figures stand flagged *reasoning-cap artefact confirmed*; the verdict without Mistral is reported beside (RESULTS.md §2) and changes nothing |
| R30 extension | **Executed**: 750 / 750 valid via StreamLake, reasoning off honoured (0 reasoning tokens), 0 parse / transport / provider failures, USD 1.27 of the 8 cap; ninth model; rule **5-of-9** |
| Scoring | `scoring/field_table.{json,md}`, `RESULTS.md` (nine models); 8-arm state kept |
| Draft | RUN3 re-embedded (`scripts/embed_run3.py`, new); **Essential 18 / Extended 28 / Full 47 unchanged**; audit 57 / 185 / 0; validate 7 / 7 (strict 6 / 7, therapy trait opt-in as designed) |

## Headline (nine models, 5-of-9; RESULTS.md §1–§3)

- **Reading (a), frozen literal:** **12 of 19 hold** — `summary` 9, `valence` 9, `intensity` 8, `primary` 7, `event_category` 7, `relationship` 7, `need` 7, `temporal_focus` 7, `meaning` 6, `harm` 5, `scope` 5, `action_tendency` 5 (the last three at the minimum).
- **Reading (b), R18 (decides):** **18 of 19 hold** — `self_position` 9, `bodily_sensation` 9, `summary` 9, `valence` 9, `intensity` 8, `turning_point` 7, `function` 7, `primary` / `event_category` / `relationship` / `need` / `temporal_focus` 7, `meaning` 6, `harm` 6, `attribution` 5, `coping` 5, `scope` 5, `action_tendency` 5. Only **`tether`** fails (4 of 9 under both) — R26 stands.
- **R20 closed:** `summary` holds 9 of 9 under both readings on the completed judge → comparable, Essential (no change of class; the ruling's condition is met).
- **DeepSeek V4 Pro 0813, reasoning off:** cheap-tier band (repeat met 5 / 19; agree met 15 / 19; holds `summary`, `valence`, `intensity`, plus `self_position` and `bodily_sensation` under (b)). It agrees with the majority on most fields but does not repeat its own answers without reasoning. Mean 592 output tokens, 26 s, USD 0.0017 per call.
- **Bands** (repeat met / 19; holds (a) / (b)): Gemini 4 Argon voting (19; 14 / 18), Llama 4 Maverick voting (19; 10 / 14), gpt-oss-120b voting (19; 8 / 15), Qwen3.8 between (15; 10 / 15), DeepSeek cheap-tier (5; 3 / 5), Mistral cheap-tier (5; 3 / 5; artefact), Haiku reference cheap-tier (13; 9 / 13), Sonnet re-run voting (19; 13 / 19). **P1–P4 not held** (DeepSeek now fits P1's cheap-tier picture of an open-weight arm; Llama and gpt-oss still do not).
- **R29 sensitivity (without Mistral, 5-of-8):** every verdict identical under both readings.

## Deviations logged this phase (`levers.json`, RESULTS.md §0.1)

R3-D5 (frozen field list pinned); lever 4 (stop 60 → 70 → 72 for the judge start rule; Phase A cap binding); judge completion note; `r29_probe` + `status_after`; `extension_plan_R30.executed` + note; `judge.py --cap-usd` and `--rejudge-missing`.

## Founder actions now open

1. **R29 re-run** (authorised by the probe): `probe_mistral.py`'s parameters on the whole arm — 750 calls ≈ USD 18.5; the founder sets the stop. The runner needs a one-line change to write to a separate raw directory (`raw/rerun_r29/`) and a `score.py` switch to read it; not done, because the run was not authorised within the cap.
2. **Veto window** on R18–R30 and on the two Phase A applications (R20 closed on the completed judge; R30 scored 5-of-9 with the supplement).
3. Extractor-bound tier at the cut; **v0.8.4 publish** (R1); **Anthropic direct key** capped until 2026-11-01; **push** — founder-only.

## Files to read first

`RESULTS.md` (nine models) → `RESULTS.8arm.md` (the pre-registered eight) → `levers.json` → `docs/discovery/ontology-crosswalk-2026-10/rulings-2026-10-18.md` (R18–R30 + Phase A notes) → `REPORT.md` §7.4 → `v0.9-proposal.md` §10.6.
