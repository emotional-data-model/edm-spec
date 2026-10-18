# STATUS — overnight delegated run, 2026-10-18 → 19 (Phases A / B / C)

**Nothing pushed.** All commits local on `discovery/ontology-crosswalk` (edm-spec) and a docs-only commit in `deepadata-com`. **`schema/` and `examples/` untouched. The founder's archive was not used in any phase.** Every phase checkpointed; no phase failed.

| Phase | Instruction | Result | Spend | Commits |
|---|---|---|---|---|
| **A** finish run 3 (cap USD 15) | judge to completion, R20, R29 probe, R30 extension + supplement, re-score, rebuild, docs | **Done.** Judge 150 / 150 both groups → **R20 closed** (`summary` comparable); **R29** probe 10 / 10 parsed → re-run branch triggered, **re-run deferred** (≈ USD 18.5, over the cap; founder sets the stop); **R30** extension (reasoning off honoured, 750 / 750, USD 1.27) + supplement (USD 9.35) → **5-of-9**, DeepSeek cheap-tier; **12 of 19 hold (a) / 18 of 19 (b); `tether` alone fails**; Essential 18 / Extended 28 / Full 47 unchanged; audit 57 / 185 / 0; 7 / 7 valid | **USD 14.09** | `c00a44a`, `792dacd`, `ed0391b`, `843c62e` |
| **B** human anchor on GoEmotions (cap USD 10) | 1,000 comments with rater annotations, pre-register + freeze, three extractors × 3 repeats, κ vs majority / vs each rater / human–human | **Done.** Frozen `5ac5169`; 450 calls; **`primary`: model–human κ 0.23–0.27 against a human–human range [0.25, 0.43]** (Sonnet and gpt-oss just below, Gemini within); **`valence`: 0.35–0.41 against [0.37, 0.53]** (Gemini and gpt-oss within, Sonnet below); P1–P5 not held; seams: `other`/`neutral`, `wonder`, `tenderness`/`reverence` | **USD 2.14** | `5ac5169` (freeze), Phase B result commit |
| **C** reading-layer discovery (no API) | literature, 25–35 cues, schema sketch, run-4 plan | **Done.** `docs/discovery/reading-layer-2026-10/`: `literature.md`, `cues-v1.md` (35 cues), `schema-sketch.md` + `reading.fragment.json` (ajv-compiles), `experiment-plan-run4.md` (not frozen, not run; private arm deferred), samplers (public tested; private written, not run) | 0 | `b943710` |

**Total API spend this night: USD 16.23** (OpenRouter billed; credit 100, ≈ 65.7 used in all). Anthropic direct: 0 (key capped to 2026-11-01).

## Deviations and tooling changes (all logged)

- **R3-D5** — the run-3 scripts derived the frozen 19-field list from the live draft, which lost `tether` under R26; pinned in `build_prompts.py` (prompts unchanged, `--check` passes).
- **Lever 4** — run-3 stop 60 → 70 → 72 so `judge.py`'s 9-reserve start rule served the last calls; the Phase A cap was binding. `judge.py` gained `--cap-usd` and `--rejudge-missing` (15 supplement texts failed on OpenRouter 429 and were re-served).
- `scripts/embed_run3.py` (new) regenerates the draft's `RUN3` literal from `field_table.json`; the former scratch generator is no longer needed.
- `score.py` / `results_md.py`: R29 sensitivity column (verdict without Mistral); §0.1 rows for the judge completion, the probe and the extension.
- OpenRouter rate limits on this account bite at ≈ 5 concurrent calls; every job ran at concurrency ≤ 4.

## Founder decisions now open

1. **R29 re-run** of the Mistral arm under the probe's parameters (≈ USD 18.5; needs a separate raw directory and a `score.py` switch, one line each; not written because not authorised within the cap).
2. **Veto window** on R18–R30 and on the Phase A applications (R20 closed; R30 scored 5-of-9).
3. **Human anchor:** whether `emotion.primary` / `valence` carry a `human_anchor` annotation (figures above); whether the three mapping seams get vocabulary notes.
4. **Reading layer:** `experiment-plan-run4.md` §11 (admit `reading` to the composites or score as a sidecar; voters; field set; thresholds; private-arm conditions and seed) and `schema-sketch.md` §7 (seal, quote privacy, SKOS).
5. Extractor-bound tier at the cut; **v0.8.4 publish** (R1); **push** everything (`edm-spec` branches, `deepadata-com` docs).

## Files to read first

`experiments/2026-10-18-run3/STATUS.md` → `experiments/2026-10-18-anchor/STATUS.md` → `docs/discovery/reading-layer-2026-10/README.md` → `deepadata-com/planning/session_handoffs/2026-10-19-edm-spec-overnight.md`.
