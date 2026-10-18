# STATUS — run 3 (2026-10-18)

**Nothing was pushed.** All work is in local commits on `discovery/ontology-crosswalk` of `edm-spec` plus a docs-only commit in `deepadata-com` (`planning/STATE.md` + session handoff). `schema/` and `examples/` untouched on every branch.

## Gates

| Gate | Requirement | Result |
|---|---|---|
| Freeze before any call | commit `run 3 pre-registration frozen` before the first call | **Passed.** `974408e` (plan amended per the founder's run-3 instruction: Sonnet re-run in the main run, stop 50, gate order, weights status, endpoint pins; Anthropic direct key found capped and the three Claude models pinned through OpenRouter at freeze). Scaffold `cc96aee`; first call (pilot) after both |
| Prompt check | committed prompt equals the draft-schema generation (`build_prompts.py --check`) | **Passed** before every run |
| Corpus identity | every text's sha256 equals the manifest | **Passed** (150 / 150) |
| Pilot | 24 calls, projection against the stop | **Three passes, 51 calls, USD 0.77.** Pilot 1 projected 117.5 (DeepSeek's first-party endpoint blocked by the account's data-policy guardrail; Qwen / Mistral / DeepSeek reasoning 8–17 k tokens per call). Lever 1 (effort low; token cap for Mistral) → 70.0. Lever 2 → stop 60. Lever 3 → DeepSeek dropped (13.32 vs Qwen 13.31) → 56.7 ≤ 60 |
| Hard stop (USD 60 in force; credit USD 50) | projection every 1,000 calls | **Passed** against the stop (final extraction 43.46); **the credit ceiling bit during the judge pass** (below) |
| Extraction | 7 arms × 750 calls, checkpointed, provider recorded | **Passed.** 5,250 / 5,250 records; 0 provider mismatches; 147 OpenRouter 429 transport failures (Sonnet 87, Gemini 60) re-requested once (R3-D3); Mistral 115 truncated outputs (max_tokens inside mandatory reasoning) stay failed repeats; Qwen 3, gpt-oss 7 unparsable |
| Judge | 300 Opus 5.5 calls (2 per text) | **Incomplete: credit exhausted.** 190 judged (four-field group 124 of 150 texts; `summary` 66 of 150); 0 malformed; USD 4.94; Opus endpoint refused `reasoning: {enabled: false}` on the first call, ran at the gateway default (≈ 380 reasoning tokens per call, 0.023 per call vs run 2's 0.022). **To finish: 110 calls ≈ USD 2.6 of OpenRouter credit; `judge.py` resumes from the checkpoints** |
| Scoring | frozen thresholds, 5-of-8 rule, bands, P1–P4; sensitivity beside | **Done** (`scoring/field_table.{json,md}`, `RESULTS.md`) |

**Spend:** USD 49.17 of the 50 credit (extraction 43.46, pilot 0.77, judge 4.94); OpenRouter reports 49.30 used. Stop in force 60 (lever 2).

## Headline (RESULTS.md §1–§3)

Frozen rule, 5-of-8: **9 of 19 hold** across the market (`primary` 7, `valence` 8, `intensity` 7, `event_category` 7, `relationship` 7, `need` 7, `temporal_focus` 7; `scope` and `action_tendency` at the minimum 5). **10 fail**, eight of them because the coverage clause, read literally, makes every stated-only field "uncovered" for every arm (null answers count against coverage); under the sensitivity reading (null counts as covered, run-1 convention) **17 of 19 hold**, and the two that still fail are `tether.type` (4 of 8, genuine) and `summary` (judge pass reached 66 texts). Founder decision first: Draft R18 (which reading the clause carries), then R19–R28 per field; R26 `tether` → interpretive under both readings.

Bands (repeat met / 19, holds frozen / sensitivity): Gemini 4 Argon voting (19; 12 / 17), Llama 4 Maverick voting (18; 9 / 13), gpt-oss-120b voting (19; 6 / 14), Qwen3.8 2.4T between (15; 7 / 14), Mistral Large 4 cheap-tier (5; 2 / 4), Haiku 5.5 reference cheap-tier (13; 7 / 12), Sonnet 5.5 re-run voting (19; 10 / 18). **All four pre-registered predictions not held**: the open-weight arms repeat like the frontier and disagree (P1 ×); Gemini holds 12 < 15 under the frozen coverage rule (P2 ×; 17 under the sensitivity); the failing set is the stated-only tier, not the borderline coded fields (P3 ×); only gpt-oss leaves `intensity.value` null on ≥ 50 % of texts (P4 ×). Framing bound (Sonnet 47-field vs 19-field): κ 0.65–0.97 coded, 0.74–0.98 free text; gpt-oss's κ 0.08 / 0.15 / 0.22 on `scope` / `action_tendency` / `tether` are vendor readings, not framing.

## Founder decisions now open

1. **Draft R18** — the coverage clause's reading (literal vs null-as-covered); it decides eight of the ten failures. Then **R19–R28** per field (RESULTS.md §7 / `ruling-drafts.md`); R26 `tether` is the one re-class recommended under both readings.
2. **Top up OpenRouter by ≈ USD 3** and resume `judge.py` (110 calls) so `summary` and the remaining 26 texts of the four free-text fields are judged; re-run `score.py` / `results_md.py`. Until then `summary`'s failure is a coverage artefact (R20).
3. **R29 Mistral Large 4** (re-run with an honoured reasoning budget before any vendor reading) and **R30 DeepSeek V4 Pro** (one-arm extension, ≈ USD 6–13).
4. **Anthropic direct key** capped until 2026-11-01; raise the console limit or keep routing through OpenRouter.
5. **Publish v0.8.4** (R1, still open) and **push** (`deepadata-com` docs commits; `edm-spec` branches) — founder-only.

## Files to read first

`experiments/2026-10-18-run3/RESULTS.md` → `levers.json` (every deviation) → `docs/discovery/ontology-crosswalk-2026-10/experiment-plan-run3.md` §7 / §9 / §12 → `REPORT.md` §7.4.
