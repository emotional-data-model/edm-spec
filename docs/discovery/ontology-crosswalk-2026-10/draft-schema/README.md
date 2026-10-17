# Draft v0.9 schema (discovery; not normative)

Generated 2026-10-17 by `../scripts/draft_schema_build.py` from the field map in `../scripts/v09_layout.py`. Nothing here is under `VERSIONING_POLICY.md`; the published `schema/` is untouched. Regenerate rather than hand-edit.

| File | Content |
|---|---|
| `fragments/common.json` | Shared shapes: `coding` (FHIR R4 Coding + EDM `relation` + optional `confidence`), `coded` (`{text, codings[]}`), `dimension` (`{text, value, codings[]}`) |
| `fragments/narrative.json` | 12 fields (v0.8.3 `core` + the narrative fields of `constellation` / `milky_way`); `arc` is a list (max 3); `self_position` is stated-only free text |
| `fragments/emotion.json` | 12 fields; `valence`, `arousal`, `intensity`, `appraisal.urgency`, `appraisal.control` are dimensions with bounded `value` |
| `fragments/context.json` | 8 fields; `scope` = `{text, direction, codings}` |
| `fragments/salience.json` | 10 fields; `tether` = `{type: coded, referent, stake}`, `persistence` = `{text, decay, codings}` |
| `fragments/motivation.json` | 5 coded fields |
| `fragments/trait.json` | Opt-in `attachment_style`, `regulation_state`; in no canonical composite |
| `fragments/telemetry.json` | v0.8.0 telemetry + `field_confidence` (object keyed by field path, values 0..1); `extraction_provider` enum widened with `google`, `open_weight`, `other` for the experiment runs |
| `edm.v0.9.essential.schema.json` | 11 affective fields: 7 narrative (`subject`, `trigger`, `harm`, `drive`, `integration`, `arc`, `self_position`) + 4 emotion (`primary`, `secondary`, `valence`, `intensity`); all 11 required keys (nullable) |
| `edm.v0.9.extended.schema.json` | 30 affective fields (every carried field whose v0.8.3 source was in Extended, plus `self_position`) |
| `edm.v0.9.full.schema.json` | 47 affective fields + `system`, `crosswalks` |

Conventions:

- Draft-07 throughout, as the published schemas. `$id` base is `https://deepadata.com/schemas/edm/v0.9.0-draft/`; the composites reference the unchanged v0.8.0 fragments (`governance`, `system`, `crosswalks`, `extensions`) by their published `$id`, so a validator registers both directories locally (see `../scripts/validate_synthetic.mjs`; no network).
- Each composite narrows a domain fragment with `allOf: [{$ref}, {propertyNames: {enum}, required}]`, so one fragment serves all profiles and the profile manifest is visible in the composite (`x_affective_fields`).
- **Value words are unchanged and canonical lists are recommended, not enforced on `text`** (`v0.9-proposal.md` §4 rule 3): every coded field lists `x_recommended_values` and, where applicable, `x_deprecated_values`. What *is* enforced: a coding whose `system` is the field's EDM vocabulary (`https://emotionaldatamodel.org/vocab/<field>/v1`) must use a code from that vocabulary (canonical plus deprecated values), so a canonical claim is checkable while free text stays legal. The v0.8.3 composites enforce strict enums on 18 of these fields; this is a loosening and is listed as a decision below.
- Rule 1 (text mandatory when populated) is enforced on `coded` and `dimension`: a non-empty `codings` array requires `text` (or, for a dimension, `text` or `value`).
- `meta.version` accepts `0.9.x` and `0.9.x-draft`. `extensions` is optional in all three composites because the migration preserves cut and out-of-profile text there; the published v0.8 composites do not list `extensions` at all, although the fragment exists.
- Trait opt-in: a partner manifest listing `trait.*` resolves to `base composite + fragments/trait.json`; the validator composes that at load time for the profiles in its opt-in set (therapy, as a discovery assumption). Without opt-in the block is rejected.

Validation results (2026-10-17, ajv 8, draft-07, local `$ref`), on the seven synthetic examples migrated by `../scripts/v09_layout.py`:

| Run | Result |
|---|---|
| Profile-aware migration, trait opt-in for therapy | 7/7 valid |
| Same, `--strict` (no opt-in composition) | 6/7: therapy rejected (`must NOT have additional properties (trait)`), as designed |
| Profile-agnostic migration (`../migrated-examples/unpruned/`) | 1/7: only therapy (Full + trait) passes; every other artifact fails on domains or fields outside its profile |
| Negative cases (coding without text, EDM code outside vocabulary, valence value 1.5, `field_confidence` with a non-field key, 5 arcs, `meta.version` 0.8.3) | all rejected; free text with no EDM coding accepted |

What the profile-aware migration had to relocate (verbatim, into `extensions["org.emotionaldatamodel.migration"].out_of_profile_fields`):

| Example | Relocated | Why |
|---|---|---|
| essential | `salience.retrieval_cues` (`core.echo`) | Essential has no salience domain; `echo` has no narrative home in v0.9 |
| full (canonical) | `trait.attachment_style`, `trait.regulation_state` | Full does not include `trait`; only an opted-in partner profile keeps them |
| the other five | nothing | |

Decisions this draft surfaces (in addition to `../v0.9-proposal.md` §9):

1. Whether `text` keeps strict enums where v0.8.3 had them (18 fields) or becomes recommended-vocabulary everywhere as drafted.
2. Whether Essential should carry `salience.retrieval_cues` so that `echo` survives an Essential migration without the legacy extension (7 + 4 + 1), or whether the loss to the extension is acceptable.
3. Whether `extensions` is formally added to every composite (needed by the migration guarantee; absent from the v0.8 composites).
4. Whether the partner opt-in for `trait` is expressed as composition at validation time (as here) or as a fourth published composite.
