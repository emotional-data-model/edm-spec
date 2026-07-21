# Changelog

All notable changes to the Emotional Data Model (EDM) specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.3] - 2026-07-21

Truth-only patch release (founder decision, 2026-07-21). Composite
conformance to the canonical fragments, one description correction, and
document regeneration. No field additions/removals beyond the composite
conformance fix, no enum changes, no semantic changes. Field-relevance
review is deferred to 0.9 with usage evidence.

### Fixed

- **Full composite `meta.source_timestamp` conformance**: the inline meta
  block in `edm.v0.8.full.schema.json` omitted `source_timestamp` (a legal
  field since v0.7.0, present in the canonical `schema/fragments/meta.json`)
  while declaring `additionalProperties: false` — so a full-profile artifact
  carrying `meta.source_timestamp` was strict-rejected by the composite
  since v0.8.0. The field is now mirrored from the fragment definition
  (optional, nullable). Artifacts that validated before still validate;
  artifacts carrying `source_timestamp` now validate as the fragment always
  intended.
- **Full profile field count corrected: 96 → 91.** 91 is the machine count
  of top-level fields across the 10 domains of the v0.8.3 Full composite
  (including the restored `source_timestamp`). The long-standing "96" was
  hand-arithmetic that never matched a shipped v0.8 schema (see
  deepadata-com `planning/EDM_SPEC_0.8.2_LINEAGE_FINDINGS.md`).
- **`narrative_archetype` description corrected** (description only; enum
  untouched at 12): "the structural role or literary trope" → the
  identity-archetype definition per ADR-0030. The field encodes which of
  the 12 canonical identity archetypes the subject embodies — an identity,
  not a story role.

### Added

- **`schema/crosswalks/v0.8.2_to_v0.8.3.json`** — machine changelog
  (`breaking_changes: false`, `release_class: "patch"`).
- **`docs/RELEASE-POLICY.md`** — the one-story release gate: every npm
  release must have its document candidate staged; npm + Zenodo publish
  together; no certification claim may cite a version whose document is
  not published.

### Changed

- **Whitepaper regenerated** (`releases/v0.8.3/`): Appendix A regenerated
  from the v0.8.3 spec — 12 identity archetypes with the identity-not-role
  definition; Full profile field count 91 throughout; `source_timestamp`
  attribution corrected to v0.7.0 per the crosswalk record.
- Repository metadata refreshed to v0.8.3: README.md, CITATION.cff,
  package.json, docs/RELEASE-NOTES.md.

### Migration

- None required. v0.8.2 artifacts are v0.8.3 artifacts; the composite fix
  only widens acceptance (artifacts using `meta.source_timestamp` in the
  Full profile now validate).

## [0.8.2] - 2026-06-16

*(Entry backfilled 2026-07-21 from the machine crosswalk
`schema/crosswalks/v0.8.1_to_v0.8.2.json` — v0.8.2 shipped to npm with no
human-facing changelog entry.)*

Schema-reconciliation patch: brings the published JSON Schema fragments
into alignment with the canonical SDK zod state (ADR-0030, amended
2026-06-16: the published spec is the source of truth; this release fixes
the baseline the generation chain starts from). No fields added, removed,
or renamed.

### Changed

- **`constellation.narrative_archetype` enum reduced 13 → 12**: `mentor`
  removed. The field encodes archetypal identity, not story role; `mentor`
  is a role. The SDK was already at 12; the published fragment lagged.
  Strictly, an artifact carrying `narrative_archetype = "mentor"` fails
  v0.8.2 validation — but no pipeline-conformant v0.8.1 artifact emitted
  it.
- **`impulse.motivational_orientation` enum expanded 5 → 6**:
  `authenticity` added (present in the SDK and whitepaper; missing from
  the published fragment). Additive.
- **`meta.profile` fragment reconciled to the two-tier model**: the shared
  `meta.json` fragment moved from a strict enum
  (`essential | extended | full | null`) to
  `oneOf(canonical enum, "partner:" pattern)`, matching what the composite
  profile schemas had already accepted since v0.8.0 (ADR-0017). The stale
  `null` member was dropped.
- **`meta.tags` spurious enum removed**: the fragment carried a bogus
  `enum: ["Short tokens", "lowercase recommended"]` (a human hint
  mis-encoded as a machine constraint) that rejected all real tags. Tags
  are again a free string array; the guidance survives in `x_constraints`.

### Added

- **`x-edm-canonical` extension property** on seven two-tier free-text
  fields (`emotion_primary`, `narrative_arc`, `relational_dynamics`,
  `arc_type`, `tether_type`, `recurrence_pattern`, `coping_style`) — the
  machine-readable preferred-vocabulary list read by the field-block
  generator. `x-` prefixed: validators ignore it; no validation change.
- **Spec-level field-block generator**
  (`scripts/generate-field-blocks.mjs`), ported from the SDK — downstream
  prompt field-blocks now generate from the spec.
- **Machine crosswalks** `v0.8.0_to_v0.8.1.json` and
  `v0.8.1_to_v0.8.2.json`.
- **npm publication**: `edm-spec` published to npm (0.8.1, then 0.8.2) —
  downstream repos consume the spec as a versioned dependency instead of
  manual copies.

### Errata

- `meta.version` constraint annotation corrected from the stale "0.6.x"
  text to the v0.8 line (annotation-only; no validation change).
- Partner example artifacts migrated to v0.8.2 stamps.
- **Known gap, resolved in 0.8.3**: v0.8.2 shipped with no human-facing
  document — CHANGELOG/RELEASE-NOTES/README stopped at 0.8.1, and the
  published v0.8.1 whitepaper describes a 14-value `narrative_archetype`
  ("structural role") that the 0.8.2 machine rejects. Certification
  language was directed to cite 0.8.1 until a documented release shipped.

### Migration

- v0.8.1 artifacts remain valid under v0.8.2 unless they carried
  `narrative_archetype = "mentor"` (remap to a canonical identity
  archetype or null). All other changes are additive, widening, or
  non-validating.

## [0.8.1] - 2026-06-12

Patch release. References and errata only — zero semantic change per §11.
Reference-schema enum lists corrected for nullable-enum conformance (§5.2);
no field definitions, enumerations, or crosswalks are semantically modified.

### Added

- **Whitepaper §14.6 reference**: Sofroniew, N., Kauvar, I., Saunders, W.,
  Chen, R., et al. (2026). *Emotion Concepts and their Function in a Large
  Language Model.* Anthropic, Transformer Circuits. arXiv:2604.07729.
  (Mechanistic evidence that affective context causally influences model
  behaviour while remaining invisible in outputs.)
- **Whitepaper §14.6 reference**: Wen, D., Sun, K., & Wang, Y. (2026).
  *A-MBER: Affective Memory Benchmark for Emotion Recognition.*
  arXiv:2604.07017. (Benchmark for evaluating affective/emotional memory
  in AI systems.)
- **Whitepaper §2.2 closing sentence**: one sentence citing Sofroniew et al.
  (2026) as direct mechanistic evidence that model-internal emotion
  representations are real, causally influence behaviour, and leave no trace
  in output text — confirming affective context cannot be governed at the
  output layer.
- **Whitepaper §11.1**: version-lineage entry for v0.8.1 (patch; references
  and errata only).
- **`releases/` directory convention**: versioned whitepaper documents now
  archived in-repo (`releases/v0.8.0/`, `releases/v0.8.1/`).

### Errata

- **Whitepaper §11.1 lineage attribution**: the paragraph incorrectly
  stated "v0.8.0 introduces Implementation Profiles"; corrected to
  "v0.6.0 introduces Implementation Profiles". Implementation Profiles
  (Essential, Extended, Full) were introduced in v0.6.0 (March 2026).
- **Whitepaper Appendix A `meta.version` constraint**: corrected from
  `MUST match "0.7.x"` to `MUST match "0.8.x"`.
- **Reference-schema nullable-enum correction (implementation conformance)**:
  24 enumerated fields across the constellation, gravity, impulse, and
  milky_way domains are nullable (`type: ["string","null"]`) per whitepaper
  §5.2 (*Population Invariants: No Omission, No Inference*), but reference
  schema enum lists did not include explicit `null`, causing spec-conformant
  artifacts with explicit-null enum fields to fail validation. Corrected in
  the ddna-tools vendored schemas (ddna-tools `fix/schema-nullable-enums`
  @ `db2c449`, 2026-06-12). Spec text unchanged — this records an
  implementation conformance correction. Reference schemas in this
  repository corrected to match (`schema/fragments/constellation.json`,
  `gravity.json`, `impulse.json`, `milky_way.json`, and inlined gravity
  fields in `edm.v0.8.extended.schema.json`).

### Changed

- **Repository metadata refreshed to v0.8.1**: README.md (was still citing
  v0.7.0 and DOI 10.5281/zenodo.19211903 throughout), CITATION.cff,
  package.json, docs/RELEASE-NOTES.md.

### Migration

- None required. v0.8.0 artifacts are v0.8.1 artifacts; no structural change.

## [0.8.0] - 2026-04-13

### Added

- **Partner Profiles (Section 3.7.6)**: Named, versioned schema declarations
  for vertical-specific field selection. Partner profile IDs use reverse-DNS
  notation (e.g., `partner:com.deepadata.journaling.v1`). Minimum 10 affective fields
  from the 57-field affective set required for certification eligibility.

- **`meta.profile` two-tier enum**: Canonical values (`essential`, `extended`,
  `full`) remain valid. Non-canonical values accepted as strings and trigger
  partner profile registry resolution. Same pattern as `arc_type`.

- **2 `arc_type` canonical values**: gratitude, authenticity (14 total, was 12)

- **Reference partner profiles**: journaling, therapy, companion, wiki
  (maintained by DeepaData as implementation examples)

### Changed

- **docs/PROFILES.md sections renumbered**:
  - 3.7.6: Partner Profiles (new)
  - 3.7.7: Profile Invariants (was 3.7.6)
  - 3.7.8: Profile Selection Guidance (was 3.7.7)

### Migration

- No breaking changes. v0.7.x artifacts remain valid.
- New `arc_type` values (gratitude, authenticity) are additive only.
- Partner profiles are optional — canonical profiles remain the default.
- See `schema/crosswalks/v0.7.0_to_v0.8.0.json` for detailed migration mapping.

## [0.7.0] - 2026-03-22

### Added

- **`arc_type` field** (constellation domain, Extended and Full profiles):
  Structural emotional arc pattern encoded at capture time.
  Canonical values: betrayal, liberation, grief, discovery, resistance, bond,
  moral_awakening, transformation, reconciliation, reckoning, threshold, exile.
  Free text accepted for novel arc types.

- **`extensions` domain** (optional, all profiles):
  Partner-namespaced semantic enrichments. Each key is a partner or platform
  identifier. Values are partner-defined objects. Extensions containing semantic
  enrichment are included in the seal hash when present at seal time.

- **`meta.source_timestamp` field**:
  Timestamp of the original source content, distinct from `created_at` which
  marks extraction time. Enables accurate temporal graph traversal.

- **3 `emotion_primary` canonical values**: disappointment, relief, frustration

- **2 `narrative_arc` canonical values**: loss, confrontation

### Changed

- **Enum fields now accept free text**: Canonical values preferred for
  cross-artifact comparability, but accuracy takes precedence over canonical
  conformance. SDK enforces preferred values via Zod union pattern.

- **`system.embeddings` description**: Clarified as platform-managed, not
  populated at extraction time, excluded from seal hash.

- **Crosswalk fields**: Clarified as optional professional mapping hooks,
  null valid in all profiles.

### Removed

- **`gravity.legacy_embed`**: Signal captured by `transformational_pivot` +
  `strength_score` + `recurrence_pattern`. Field was redundant.

- **`telemetry.alignment_delta`**: Platform feedback signal, not an artifact
  field. Moved to platform layer.

- **`system.indices.sector_weights`**: Platform-managed, always zero at
  extraction time, excluded from seal hash. Kept `waypoint_ids` only.

- **`crosswalks.HMD_v2_memory_type`**: Redundant with `memory_type` in
  constellation domain.

- **`telemetry.extraction_chunking_strategy`**: Vendor pipeline concern, not
  representational. Belongs in Extensions or vendor infrastructure.

### Migration

- Artifacts using version 0.6.x remain valid. Fields removed in v0.7.0 are
  ignored by v0.7.0 validators. New fields are optional. No breaking changes.

## [0.6.0] - 2026-03-11

### Added

- **Implementation Profiles** (FHIR-style three-schema model):
  - **Essential**: 5 domains, 24 fields — journaling apps, companion AI, minimal memory footprint
  - **Extended**: 7 domains, 50 fields — therapy apps, memory platforms, relational context
  - **Full**: 10 domains, 96 fields — clinical applications, research, full affective context

- **Conformance Levels**:
  - **Compliant**: Passes JSON Schema validation for declared profile
  - **Sealed**: Compliant + cryptographically signed .ddna envelope
  - **Certified**: Sealed + issuer in DeepaData trust registry

- **`meta.profile` field**: Required field declaring implementation profile (`essential` | `extended` | `full`)

- **Canonical schema hosting**: Schemas served at `https://deepadata.com/schemas/edm/v0.6.0/`

- **9 enum additions across 5 fields** (v0.5.1 → v0.6.0 via SDK evaluation):
  - `emotion_primary`: +1 (shame)
  - `relational_dynamics`: +4 (grandparent_grandchild, friend, colleague, couple)
  - `tether_type`: +1 (self)
  - `motivational_orientation`: +1 (authenticity)
  - `narrative_archetype`: +1 (orphan)

### Changed

- **VitaPass rename**: `meta.aura_id` renamed to `meta.vita_pass` (subject identifier)
- **Profile Completeness**: `governance.profile_completeness` replaces `governance.domain_completeness`
- **Repository transfer**: Moved to `emotional-data-model` GitHub organization

### Migration

- See `schema/crosswalks/v0.5.1_to_v0.6.0.json` for detailed migration mapping
- Artifacts must declare `meta.profile` to validate against v0.6.0 schemas

## [0.5.1] - 2026-02-15

### Added

- **6 enum additions** based on SDK evaluation (CANDIDATE 004-010):
  - `emotion_primary`: +1 (shame)
  - `relational_dynamics`: +4 (grandparent_grandchild, friend, colleague, couple)
  - `tether_type`: +1 (self)
  - `motivational_orientation`: +1 (authenticity)
  - `narrative_archetype`: +1 (orphan)

### Migration

- See `schema/crosswalks/v0.5_to_v0.5.1.json` for detailed migration mapping
- Additive enum expansion only — no breaking changes

## [0.5.0] - 2026-02-09

### Added

- **14 enum additions across 5 fields** based on Phase 2 multi-provider evaluation:
  - `emotion_primary`: +5 (pride, anxiety, gratitude, longing, hope)
  - `relational_dynamics`: +5 (family, professional, therapeutic, service, adversarial)
  - `drive_state`: +3 (confront, protect, process)
  - `coping_style`: +1 (process)
  - `adaptation_trajectory`: +1 (emerging)

### Fixed

- `constellation.expressed_insight`: Removed erroneous enum values (was free text)
- `gravity.recurrence_pattern`: Fixed malformed enum value with concatenated description

### Migration

- See `schema/crosswalks/v0.4_to_v0.5.json` for detailed migration mapping
- Additive enum expansion only — no breaking changes
- v0.4.0 artifacts remain valid under v0.5.0

## [0.4.1] - 2026-01-17

*(Entry reconstructed 2026-06-12 from the `v0.4.1` git tag message and
docs/RELEASE-NOTES.md; no contemporaneous CHANGELOG entry existed.)*

### Changed

- **Envelope cryptographic model updated to W3C Data Integrity Proofs**
  (`eddsa-jcs-2022`) for the .ddna envelope.
- Schema unchanged — remains v0.4.0 (backward compatible).

### Notes

- The tag message cites DOI 10.5281/zenodo.17808652 (the concept DOI).
  No version-specific v0.4.1 Zenodo deposit exists in the concept lineage.

## [0.4.0] - 2025-12-04

### Changed

- **GOVERNANCE domain**: New top-level domain split from META
- **Field consolidation**: 102 → 96 fields (6 deleted, 6 moved to GOVERNANCE)
- **Description format**: Concise descriptions with concrete examples

### Removed

- `meta.session_id` — redundant with created_at + parent_id
- `constellation.affective_clarity` — unclear definition
- `constellation.active_motivational_state` — redundant with IMPULSE domain
- `milky_way.media_context` — overlapped with media_format
- `milky_way.memory_layers` — unclear origin
- `gravity.tether_target` — redundant with core.anchor

### Migration

- See `schema/crosswalks/v0.3_to_v0.4.json` for detailed migration mapping
- Breaking changes: GOVERNANCE domain required

## [0.3.0] - 2025-11-01

### Added

- Initial public specification
- 10 domains, 102 fields
- Closed provenance pre-release

[0.8.3]: https://github.com/emotional-data-model/edm-spec/compare/v0.8.2...v0.8.3
[0.8.2]: https://github.com/emotional-data-model/edm-spec/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/emotional-data-model/edm-spec/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/emotional-data-model/edm-spec/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.4.0...v0.5.0
[0.4.1]: https://github.com/emotional-data-model/edm-spec/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/emotional-data-model/edm-spec/releases/tag/v0.3.0
