# Release Notes — Emotional Data Model (EDM)

## EDM v0.8.0 (April 2026) — In Progress

**Branch:** `feat/v0.8.0`

- Partner Profiles (Section 3.7.6): Named, versioned schema declarations for vertical-specific field selection
- `meta.profile` two-tier enum: Canonical values plus partner profile ID support
- `meta.profile` namespace model: Partner profile IDs now declared with `partner:` prefix per ADR-0016
- `arc_type` canonical values: +gratitude, +authenticity (14 total, was 12)
- Reference partner profiles: journaling, therapy, companion, wiki
- Schema files: `edm.v0.8.{essential,extended,full}.schema.json`

See [PROFILES.md](PROFILES.md) Section 3.7.6 for Partner Profiles details.

---

## EDM v0.7.0 (March 2026) — Current

**DOI:** [10.5281/zenodo.19211903](https://doi.org/10.5281/zenodo.19211903)

- `arc_type` field: Structural emotional arc pattern (12 canonical values)
- `extensions` domain: Partner-namespaced semantic enrichments
- `meta.source_timestamp`: Original content timestamp
- Enum expansions: emotion_primary (+3), narrative_arc (+2)
- Free-text enum pattern: All enum fields accept canonical OR free text
- Schema files: `edm.v0.7.{essential,extended,full}.schema.json`

See [CHANGELOG.md](../CHANGELOG.md) for full v0.7.0 details.

---

## EDM v0.6.0 (March 2026)

- Implementation Profiles: Essential (24 fields), Extended (50 fields), Full (96 fields)
- Conformance Levels: Compliant, Sealed, Certified
- New field: `meta.profile` — profile declaration at extraction time
- Only Full Profile is eligible for Certified conformance
- Schema files: `edm.v0.6.{essential,extended,full}.schema.json`

See [PROFILES.md](PROFILES.md) and [CONFORMANCE.md](CONFORMANCE.md) for details.

---

## EDM v0.5.1 (March 2026)

**DOI:** [10.5281/zenodo.18883392](https://doi.org/10.5281/zenodo.18883392)

Additive patch release with nine canonical enumeration values across five fields. These values were consistently returned by LLM extractors (Anthropic, OpenAI, Kimi) during production corpus evaluation and are semantically correct additions to the schema.

### Enum Additions

| Field | Values Added |
|-------|--------------|
| `emotion_primary` | `shame` |
| `relational_dynamics` | `grandparent_grandchild`, `friend`, `couple`, `colleague` |
| `narrative_archetype` | `orphan` |
| `tether_type` | `identity`, `self` |
| `motivational_orientation` | `authenticity` |

### Notes

- Backward-compatible — existing v0.5.0 artifacts remain valid
- Schema validation updated in deepadata-edm-sdk v0.5.1
- Validated through end-to-end corpus evaluation (1,731 API calls)

---

## EDM v0.5.0 (February 2026)

**DOI:** [10.5281/zenodo.18541956](https://doi.org/10.5281/zenodo.18541956)

- Enum expansions across multiple domains
- Identity binding renamed from AuraID to VitaPass
- W3C Data Integrity Proofs (eddsa-jcs-2022) for .ddna envelope
- MIT License adopted for open specification

---

## EDM v0.4.0 (December 2025)

- Initial public release
- Core schema specification (10 domains, 96 fields)
- .ddna envelope format defined
- Affective manifold foundations

---

## EDM v0.3-pre (November 2025)

- Canonical schema finalized: `schema/edm.v0.3.schema.json`
- Fragments aligned (informative)
- Crosswalks added for v0.1 → v0.2 → v0.3 migration
- Provenance chain: DeepaData-v1 → DeepaData-v2 → deepadata-edm-spec

---

## Version Lineage

| Version | Date | Status |
|---------|------|--------|
| v0.8.0 | April 2026 | **In Progress** |
| v0.7.0 | March 2026 | **Current** |
| v0.6.0 | March 2026 | Published |
| v0.5.1 | March 2026 | Published |
| v0.5.0 | February 2026 | Published |
| v0.4.0 | December 2025 | Published |
| v0.3-pre | November 2025 | Pre-release |

---

© 2025–2026 DeepaData Pty Ltd — Released under MIT License.
