# Release Notes — Emotional Data Model (EDM)

## EDM v0.8.3 (July 2026) — Current

**DOI:** pending — new Zenodo deposit is a founder action; the latest
published deposit remains v0.8.1 (10.5281/zenodo.20678017), and the
concept DOI [10.5281/zenodo.17808652](https://doi.org/10.5281/zenodo.17808652)
always resolves to the latest published version.

Truth-only patch release (founder decision, 2026-07-21). No enum changes,
no semantic changes; field-relevance review deferred to 0.9.

### Fixed

- **Full composite `meta.source_timestamp` conformance**: the Full
  composite's inline meta block omitted `source_timestamp` (canonical since
  v0.7.0) under `additionalProperties: false`, strict-rejecting a legal
  field since v0.8.0. Now mirrored from the canonical meta fragment
  (optional, nullable). Widening only — everything that validated before
  still validates.
- **Full profile field count: 96 → 91** (machine count of the composite's
  top-level fields; "96" was hand-arithmetic that never matched a shipped
  v0.8 schema).
- **`narrative_archetype` description**: corrected to the
  identity-archetype definition per ADR-0030 (identity, not structural
  role). Enum untouched at 12.

### Added

- `schema/crosswalks/v0.8.2_to_v0.8.3.json` (machine changelog)
- `docs/RELEASE-POLICY.md` — the one-story release gate

### Changed

- Whitepaper regenerated (`releases/v0.8.3/`): Appendix A from the v0.8.3
  spec (12 identity archetypes, identity-not-role definition), field count
  91 throughout, `source_timestamp` attribution corrected to v0.7.0
- Repository metadata refreshed (README, CITATION.cff, package.json)

See [CHANGELOG.md](../CHANGELOG.md) for the enumerated change list.

---

## EDM v0.8.2 (June 2026)

**DOI:** none — npm-only release; no Zenodo deposit and no standalone
document shipped (gap recorded and closed by the 0.8.3 release and
`docs/RELEASE-POLICY.md`).

Schema-reconciliation patch aligning the published fragments with the
canonical SDK zod state (ADR-0030, amended 2026-06-16):

- `narrative_archetype` enum 13 → 12 (`mentor` removed; identity, not role)
- `motivational_orientation` enum 5 → 6 (`authenticity` added)
- `meta.profile` fragment reconciled to the two-tier model
  (canonical enum | `partner:` pattern; stale `null` dropped)
- `meta.tags` spurious enum removed (bug fix — it rejected all real tags)
- `x-edm-canonical` preferred-vocabulary annotation added to 7 two-tier
  fields (non-validating)
- Spec-level field-block generator; machine crosswalks; first npm
  publications (0.8.1, 0.8.2)

Machine changelog: `schema/crosswalks/v0.8.1_to_v0.8.2.json`.

---

## EDM v0.8.1 (June 2026)

**DOI:** 10.5281/zenodo.20678017

Patch release — references and errata only, zero semantic change per §11.

### References added

- Whitepaper §14.6: Sofroniew, N., Kauvar, I., Saunders, W., Chen, R.,
  et al. (2026). *Emotion Concepts and their Function in a Large Language
  Model.* Anthropic, Transformer Circuits. arXiv:2604.07729
- Whitepaper §14.6: Wen, D., Sun, K., & Wang, Y. (2026). *A-MBER: Affective
  Memory Benchmark for Emotion Recognition.* arXiv:2604.07017
- Whitepaper §2.2: one closing sentence citing Sofroniew et al. as mechanistic
  evidence that affective context cannot be governed at the output layer

### Errata

- **§11.1 lineage attribution**: "v0.8.0 introduces Implementation Profiles"
  corrected to "v0.6.0 introduces Implementation Profiles" (v0.6.0 is the
  release that introduced Essential/Extended/Full profiles)
- **Appendix A `meta.version` constraint**: corrected from `"0.7.x"` to
  `"0.8.x"`
- **Reference-schema nullable-enum correction** (24 fields; implementation
  conformance to §5.2 — spec text unchanged; schema fix staged)

### Other

- Repository metadata refreshed (README, CITATION.cff, package.json)
- No schema changes; no crosswalk required

See [CHANGELOG.md](../CHANGELOG.md) for the enumerated change list.

---

## EDM v0.8.0 (April 2026)

**DOI:** [10.5281/zenodo.19555166](https://doi.org/10.5281/zenodo.19555166)

- Partner Profiles (Section 3.7.6): Named, versioned schema declarations for vertical-specific field selection
- `meta.profile` two-tier enum: Canonical values plus partner profile ID support
- `meta.profile` namespace model: Partner profile IDs declared with `partner:` prefix per ADR-0017. Canonical profiles unchanged.
- `arc_type` canonical values: +gratitude, +authenticity (14 total, was 12)
- Reference partner profiles: journaling, therapy, companion, wiki
- Schema files: `edm.v0.8.{essential,extended,full}.schema.json`

See [PROFILES.md](PROFILES.md) Section 3.7.6 for Partner Profiles details.

---

## EDM v0.7.0 (March 2026)

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

| Version | Date | Status | Zenodo DOI |
|---------|------|--------|------------|
| v0.8.3 | July 2026 | **Current** | pending (founder deposit) |
| v0.8.2 | June 2026 | Published (npm only; no Zenodo deposit) | — |
| v0.8.1 | June 2026 | Published | 10.5281/zenodo.20678017 |
| v0.8.0 | April 2026 | Published | 10.5281/zenodo.19555166 |
| v0.7.0 | March 2026 | Published | 10.5281/zenodo.19211903 |
| v0.6.0 | March 2026 | Published | 10.5281/zenodo.18951891 |
| v0.5.1 | March 2026 | Published | 10.5281/zenodo.18883392 |
| v0.5.0 | February 2026 | Published | 10.5281/zenodo.18541956 |
| v0.4.1 | January 2026 | Published (no separate Zenodo deposit) | — |
| v0.4.0 | December 2025 | Published | 10.5281/zenodo.17808653 |
| v0.3-pre | November 2025 | Pre-release | — |

**Concept DOI (all versions):** [10.5281/zenodo.17808652](https://doi.org/10.5281/zenodo.17808652)

Note: the v0.8.0 deposit (10.5281/zenodo.19555166) was created as a separate
Zenodo concept (19555165) rather than as a new version under 17808652. The
v0.8.1 deposit reunifies the lineage by publishing as a new version of record
19211903 (v0.7.0) within concept 17808652. The orphaned v0.8.0 record is
cross-linked via related identifiers.

---

© 2025–2026 DeepaData Pty Ltd — Released under MIT License.
