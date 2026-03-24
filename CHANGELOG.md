# Changelog

All notable changes to the Emotional Data Model (EDM) specification are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.7.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/emotional-data-model/edm-spec/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/emotional-data-model/edm-spec/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/emotional-data-model/edm-spec/releases/tag/v0.3.0
