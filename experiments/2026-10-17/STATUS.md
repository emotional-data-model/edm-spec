# STATUS — overnight run 2026-10-17/18

**Nothing was pushed.** All work is in local commits on two branches of `edm-spec` plus a docs-only commit in `deepadata-com` (planning/STATE.md + session handoff).

## Phases and gates

| Phase | Gate | Result |
|---|---|---|
| Setup | `.env` untracked and ignored; three providers authenticate; models pinned | `.env` was untracked but **not in `.gitignore`**; rather than abort the run it was added (`.env`, `.env.*`, `__pycache__/`) on both branches. All three providers authenticated (4 extractors, minimum 3 met). Pins: `claude-sonnet-5-5`, `claude-haiku-5-5`, `gpt-6.1-sol`, `kimi-k2.6`; judge `claude-opus-5-5` (`experiments/2026-10-17/models.json`). |
| 0 — release/0.8.4 | examples 7/7 valid; field-count script in CI; docs patched; committed | **Done.** Branch `release/0.8.4` from `main`: `bb84930` (patch) + `33ea740` (residuals). `npm run validate` 7/7; `node scripts/count-fields.mjs` 31/62/91 available, 20 required, Extended 7 domains. Worktree removed; branch kept. Not tagged, not published. |
| 1a — rulings | draft schema rebuilt; v09 validation 7/7 | **Done.** `1e27a9b` on `discovery/ontology-crosswalk`. Essential = 12; `extensions` in all composites; coded `text` = recommended vocabulary, codings validated. 7/7 valid (strict mode 6/7, trait opt-in as designed). |
| 1b/1c — pre-registration | commit `pre-registration frozen` exists before any extraction call | **Done.** `c4804ff`. Thresholds verbatim, three arms of 50, prompts and prices recorded. LoCoMo (CC BY-NC 4.0) referenced by path only; LongMemEval (MIT) also by path; Pepys committed. |
| 2 — extraction | 3,000 calls checkpointed; projection ≤ USD 80 | **Done.** `99fabed`. 3,000 / 3,000 valid JSON outputs; USD 27.84; 0 transport failures. Pilot 12 calls (USD 0.27) + 2 Kimi probes. Deviation D1: Kimi K2.6 run with thinking disabled (plan §10). |
| 3 — scoring and write-up | RESULTS.md, REPORT §7, STATE.md, handoff | **Done.** Judge 750 calls (USD 12.44, 0 malformed), raters 720 calls (USD 1.32). `experiments/2026-10-17/RESULTS.md`; `REPORT.md` §7.1; `deepadata-com/planning/STATE.md` + `planning/session_handoffs/2026-10-18-edm-spec-overnight.md`. |

**Spend:** USD 41.95 of 80 (extraction 27.84, judge 12.44, raters 1.32, pilot 0.27, probes ≈ 0.06).

## Headline results (frozen thresholds; details in RESULTS.md)

- Per field, pooled over 150 texts: **20 pass, 4 interpretive, 28 cut** of 56 scored units; 4 numeric `value` slots never populated. Two of the passes (`narrative.integration`, borderline `identity_link`) are carried by agreement on null.
- The short narrative slots `subject / trigger / harm / drive` and the salience lists `retrieval_cues / themes / resilience` do not replicate across models; `emotion.primary`, `valence`, `event_category`, `relationship`, `tether.type`, the motivation fields, `summary`, `meaning`, `self_position`, `bodily_sensation` do.
- Repeatability is model-bound: Sonnet 5.5 meets the bar on 47 / 52 units, gpt-6.1-sol 36, Kimi K2.6 24, Haiku 5.5 15.
- Task (a) **passes** pooled, synthetic and Pepys (salience beats recency by 14–21 points pooled); **fails** on the conversational arm.
- Task (b) **fails** (12 % vs 9 % control): `self_position` stays a stated-only record; the interpretation-shift claim is withdrawn.
- Null precision: `bodily_sensation` clean; `meaning` is inferred on 62–94 % of texts that state no meaning; `self_position` leaks 7–37 % depending on model.

## Needs a founder decision

1. **Publish v0.8.4?** Branch `release/0.8.4` is complete and unpublished: merge to `main`, tag `v0.8.4`, npm publish, Zenodo deposit, then set `CITATION.cff` `date-released` / DOI. The two composite schema files carry annotation-only edits (Essential / Extended `field_count` 31 / 62 and description text; the v0.8.3 precedent for Full) — confirm this is acceptable for a documentation patch or revert those two files.
2. **v0.9 field list.** Accept the pooled pass / interpretive / cut table as the basis for the next draft, or weight the synthetic arm (which passes 23 units) differently from Pepys (10). Specific calls: cut or move to `extensions` the 28 cut units; keep the 4 interpretive fields as text with an "interpretive" marker; drop `value` from `valence`, `arousal`, `urgency`, `control`; decide whether `integration` / `identity_link` count as passes given null-driven agreement.
3. **`self_position`.** Keep as a stated-only field (it is the most repeatable free-text unit) but withdraw the "changes interpretation" rationale from `v0.9-proposal.md` §3, or cut it with `narrative_archetype`.
4. **Stated-only prompting.** `narrative.meaning` is inferred by every model; redefine (quotation-only) before any second run, or accept it as interpretive.
5. **Extractor pins.** `gpt-6.1-sol` was pinned as the OpenAI flagship because `gpt-6-astra` (USD 10 / 50) alone would exceed the budget; `kimi-k2.6` ran with thinking disabled (D1). Re-pin or re-run if the founder wants defaults or the premium tier; `kimi-k3` exists.
6. **Haiku as a rater.** Haiku 5.5 meets repeatability on 15 / 52 units and effectively makes the "≥ 3 of 4" rule "Sonnet, GPT and Kimi all pass". Keep it (the rule was frozen) or pre-register a 3-extractor design for the second run.
7. **deepadata-com commit.** STATE.md and the handoff were committed locally on `main` of `deepadata-com` (docs-only, same convention as earlier overnight sessions). Push or discard.

## Files to read first

`experiments/2026-10-17/RESULTS.md` → `docs/discovery/ontology-crosswalk-2026-10/experiment-plan.md` §4.1 / §10 → `REPORT.md` §7.1 → `releases/v0.8.4/ERRATA.md`.
