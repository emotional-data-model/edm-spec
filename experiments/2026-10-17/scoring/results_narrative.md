## 0. Summary

Run completed 2026-10-17/18, unattended, on branch `discovery/ontology-crosswalk`. 150 texts (synthetic 50, conversational 50, Pepys 50) × 4 extractors × 5 repeats = 3,000 extraction calls, all 3,000 returned a valid JSON object with the 47 fields (4 outputs lacked one key, scored as null). Judge pass: 750 Opus 5.5 calls; rater pass: 720 calls. Total spend USD 41.95 (extraction 27.84, judge 12.44, raters 1.32, pilot 0.27, two Kimi probes ≈ 0.06) of the USD 80 budget.

**Headline.** The v0.9 draft layout splits cleanly into three tiers under the frozen thresholds:

- **Reliable and comparable (pass, pooled):** 20 of 56 units — `emotion.primary`, `emotion.valence.text`, `emotion.intensity.value`, `emotion.appraisal.attribution`, `emotion.bodily_sensation`, `context.event_category`, `context.relationship`, `context.scope.text`, `salience.tether.type`, `salience.function`, `motivation.action_tendency`, `motivation.need`, `motivation.temporal_focus`, `motivation.coping`, `narrative.turning_point`, `narrative.summary`, `narrative.meaning`, `narrative.self_position`, `narrative.identity_link`, `narrative.integration`. Of these, `narrative.integration` passes only because the four models agree on *null* two-thirds of the time (populated-only cross rate 0.40) and `narrative.identity_link` is borderline the same way (0.59); the rest hold up on populated answers.
- **Repeatable within a model but not comparable across models (interpretive):** 4 units — `emotion.temporal_profile`, `salience.memory_type`, `salience.linkage_strength` (ICC 0.50 across models; gpt-6.1-sol leaves it null 90 % of the time), `motivation.risk_posture`.
- **Not repeatable (cut, or to `extensions`):** 28 units — the four short narrative slots `subject`, `trigger`, `harm`, `drive` (Sonnet 5.5 repeats them at 0.80–0.87 but no other model does, and models name different referents: cross 0.38–0.54); `narrative.valence_shift`; `narrative.arc` and `emotion.secondary` (first element; both borderline); `emotion.kind` and `emotion.arousal.text` (null ≥ 91 %); `emotion.intensity.text`; `emotion.appraisal.urgency.text` and `.control.text`; `emotion.meta`; `context.event`, `context.place`, `context.people`, `context.relationship_model`, `context.life_stage`, `context.scope.direction`; `salience.tether.referent` and `.stake`, `salience.retrieval_cues`, `salience.themes` (cross 0.06: every model lists different themes), `salience.recurrence`, `salience.persistence.text` and `.decay`, `salience.resilience`, `salience.trajectory`. Four numeric slots (`valence.value`, `arousal.value`, `urgency.value`, `control.value`) were never populated by any extractor and should lose their `value` member.

Repeatability is a property of the extractor as much as of the field: Claude Sonnet 5.5 meets the repeatability threshold on 47 of the 52 scored units that carry data, gpt-6.1-sol on 36, Kimi K2.6 on 24, Claude Haiku 5.5 on 15. With Haiku as the fourth rater, the "≥ 3 of 4" rule in practice requires Sonnet, GPT and Kimi all to pass. Cross-model agreement is the binding constraint: most coded fields that fail do so because the four models carve the vocabulary differently, not because any one of them is noisy.

**Task (a)** passes pooled (every extractor beats recency by ≥ 10 points with the pre-registered score `S_all`) and in the synthetic and Pepys arms, and fails in the conversational arm (LoCoMo and LongMemEval), where neither policy beats the random floor. **Task (b)** fails: restoring a stated `self_position` moves 12 % of rater readings of arc / trajectory / need, restoring a neutral control field moves 9 %; the claim that `self_position` changes downstream interpretation is dropped from the proposal, while the field itself stays a legitimate stated-only record.

**Interpretation-only.** Null precision on the synthetic ground truth separates the stated-only fields sharply. `emotion.bodily_sensation` is null on 98–100 % of texts that state no sensation and populated on 100 % of texts that do. `narrative.meaning` is the opposite: every extractor writes a meaning for 62–94 % of texts that state none. `narrative.self_position` leaks on 7–37 % of "no" texts depending on the model; `salience.function` on 5–69 %. These are prompt / definition problems (the fields invite a summary rather than a quotation) and are reported, not fed into the pass / cut rule, per §4.4.

## 0.1 Deviations from the pre-registration

| # | Deviation | Why | Logged |
|---|---|---|---|
| D1 | `kimi-k2.6` run with `thinking: {type: disabled}` instead of provider defaults | its default reasoning consumed the 8,000-token output cap with no JSON on 3 / 3 pilot calls; at 32,000 tokens it used ≈ 10k reasoning tokens, 126 s and USD 0.049 per call, projecting ≈ USD 85 total | plan §10 before the main run; commit 6f6f119 |
| D2 | Anthropic prompt cache TTL set to the 5-minute default (the runner initially requested 1 h) | the 1-hour write price (2 × input) did not match `models.json` (1.25 ×); changes cost only | plan §10 |
| D3 | Judge and rater spend recorded in `spend_judge.json` and `spend_rater.json`, not `spend.json` | the two passes ran concurrently and would have overwritten one ledger | this file |
| D4 | Four extraction outputs (3 Haiku, 1 Sonnet) returned 46 of the 47 keys | missing key scored as null (the plan counts only non-JSON outputs as failed repeats) | this file |
| D5 | `narrative.turning_point` scored as "populated" only when `true` for null precision | the plan's wording ("populated value") is ambiguous for a boolean; `false` and null both mean "no turning point stated" | this file |

No threshold, field list, corpus text, prompt or model was changed after the first extraction call.

## 0.2 Limitations

- The judge is a model (Opus 5.5), not a human; free-text agreement is "agreement as read by Opus 5.5". The judge saw the source text and all answers for a field at once, which may make it lenient toward paraphrase.
- Pepys back-references are lexical (shared distinctive terms), not hand-coded; the Pepys task (a) result is a result about that proxy.
- LongMemEval blocks contain two named sessions each, so hit rates move in steps of 0.5; three blocks cannot distinguish policies finely. LoCoMo probes are evenly spread across sessions, so the probe-level hit rate is near k/n for any policy.
- The synthetic arm was authored by one model (Claude Fable 5.1) to a design matrix; its texts state flags explicitly and may be easier than organic text, which the per-arm tables make visible (synthetic passes more units than the other arms).
- Kimi K2.6 ran without thinking (D1); its repeatability may differ from its default-mode behaviour.
- Single run; no re-run of "interpretive" fields with tightened definitions was made (the plan reserves that for a second, reported run).
