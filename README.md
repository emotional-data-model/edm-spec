# Emotional Data Model (EDM) Specification

**Current Version:** v0.8.3
**Released:** July 2026
**DOI:** [10.5281/zenodo.21490478](https://doi.org/10.5281/zenodo.21490478) (this version) · [10.5281/zenodo.17808652](https://doi.org/10.5281/zenodo.17808652) (concept — resolves to latest)

## 📄 Official Whitepaper

The EDM whitepaper is archived in-repo under [`releases/`](releases/) and published on Zenodo:
- **Download:** [EDM v0.8.3 Whitepaper (PDF)](https://doi.org/10.5281/zenodo.21490478)
- **Cite as:** Harvey, J. (2026). Emotional Data Model (EDM). Zenodo. https://doi.org/10.5281/zenodo.17808652

## 🔧 Implementation

This repository contains:
- Profile-based JSON Schemas (`schema/edm.v0.8.{essential,extended,full}.schema.json`)
- Example artifacts (`examples/`)
- Implementation documentation (`docs/`)
- Release notes

Reference implementations:
- [ddna-tools](https://github.com/emotional-data-model/ddna-tools) - Sealing and verification
- [deepadata-edm-sdk](https://github.com/deepadata/deepadata-edm-sdk) - Artifact extraction
- [deepadata-edm-mcp-server](https://github.com/deepadata/deepadata-edm-mcp-server) - MCP adapter

---

# Emotional Data Model — EDM (Specification)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21490478.svg)](https://doi.org/10.5281/zenodo.21490478)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.8.3-green.svg)](https://github.com/emotional-data-model/edm-spec/releases/tag/v0.8.3)
[![Status](https://img.shields.io/badge/status-Stable-brightgreen.svg)]()

**Status:** Stable (v0.8.3) — Production ready

---

## Why EDM Exists

**Everyone is building memory for AI. No one is building identity governance for emotional data.**

As AI agents gain persistent memory (Mem0, OpenAI Memory, etc.) and communicate via standardized protocols (MCP, A2A), a critical gap remains: **there is no governance-first standard for emotional data**.

EDM fills this gap by providing:
- A **portable schema** for emotional context (not locked to any vendor)
- **Compliance by design** (GDPR, HIPAA, EU AI Act ready)
- **Non-inferential representation** (explicit data only, no psychological reconstruction)
- The foundation for **.ddna** — a cryptographically-signed emotional identity artifact

---

## Scope and Non-Goals

**EDM is:** A data format specification. It defines structure and semantics for emotional context that can be validated, exchanged, and governed.

**EDM is not:**
- An identity provider (Auth0-class systems remain external)
- A certificate authority or regulator
- A memory store, agent runtime, or analytics system
- An emotion recognizer or prediction system

**Tooling is non-normative.** Any tooling built around EDM (validators, SDKs, CLI tools) is reference implementation only. The canonical JSON Schema remains the sole source of truth.

**See:** [Scope and Non-Goals](docs/SCOPE_AND_NONGOALS.md) | [EDM and .ddna Boundary](docs/EDM_DDNA_BOUNDARY.md)

---

## Official Publication

The EDM whitepaper is published on Zenodo (latest published deposit:
v0.8.1; the v0.8.3 document is regenerated in-repo under
`releases/v0.8.3/` and its Zenodo deposit is pending):

**Citation:**
> Harvey, J. (2026). Emotional Data Model (EDM). Zenodo. https://doi.org/10.5281/zenodo.17808652

**Full Whitepaper:** [Download from Zenodo](https://doi.org/10.5281/zenodo.20678017)

---

## Overview

The **Emotional Data Model (EDM) v0.8.3** is a governance-first schema for representing emotional context in AI systems. It defines a domain-complete, schema-bound format that externalizes affective context as a deterministic, model-agnostic data object.

**New in v0.8.x:** Partner Profiles (§3.7.6), `meta.profile` two-tier model with `partner:` prefix, two new arc_type values, certification minimum bar. v0.8.1 is a references/errata patch; v0.8.2 reconciles the published fragments with the canonical vocabulary (ADR-0030 — `narrative_archetype` at 12 identity archetypes); v0.8.3 is a truth-only patch (Full composite `source_timestamp` conformance, field count 91, document regeneration). See [PROFILES.md](docs/PROFILES.md), [CONFORMANCE.md](docs/CONFORMANCE.md), and [CHANGELOG.md](CHANGELOG.md).

**Key principles:**
- **Transient by default** — EDM artifacts should not persist beyond session windows (24 hours max) unless explicitly sealed in a .ddna envelope
- **Non-inferential** — No field may contain psychological inference or behavioral prediction
- **Portable** — Works across any LLM provider, memory system, or agent framework
- **Compliant** — Built for GDPR, CCPA, HIPAA, EU AI Act from day one

This repository contains:

- Canonical JSON Schema for EDM v0.8
- Domain Fragment Schemas (10 domains, 91 fields, Full profile)
- Implementation Profiles and Conformance documentation
- Migration Crosswalks and Guides
- Validation Tools & Examples

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/emotional-data-model/edm-spec.git
cd edm-spec

# Validate an artifact (choose profile schema)
npm install -g ajv-cli
ajv validate -s schema/edm.v0.8.full.schema.json -d examples/example-full-profile.json
ajv validate -s schema/edm.v0.8.essential.schema.json -d examples/example-essential-profile.json
```

### Canonical Schema URLs

Profile schemas are hosted at their canonical `$id` URLs:

```
https://deepadata.com/schemas/edm/v0.8.0/edm.essential.schema.json
https://deepadata.com/schemas/edm/v0.8.0/edm.extended.schema.json
https://deepadata.com/schemas/edm/v0.8.0/edm.full.schema.json
```

For always-latest versions, use `/current/` (redirects to latest stable):

```
https://deepadata.com/schemas/edm/current/edm.essential.schema.json
https://deepadata.com/schemas/edm/current/edm.extended.schema.json
https://deepadata.com/schemas/edm/current/edm.full.schema.json
```

### Using in Your Project

**JavaScript/TypeScript:**
```javascript
// Import the profile schema matching your artifact's meta.profile
import essentialSchema from 'edm-spec/schema/edm.v0.8.essential.schema.json';
import extendedSchema from 'edm-spec/schema/edm.v0.8.extended.schema.json';
import fullSchema from 'edm-spec/schema/edm.v0.8.full.schema.json';
import Ajv from 'ajv';

const ajv = new Ajv();
const validate = ajv.compile(fullSchema); // or essentialSchema, extendedSchema

if (validate(artifact)) {
  console.log('Valid EDM v0.8 artifact');
} else {
  console.error('Validation failed:', validate.errors);
}
```

**Python:**
```python
import json
import jsonschema

# Choose profile schema matching artifact's meta.profile
with open('schema/edm.v0.8.full.schema.json') as f:
    schema = json.load(f)

with open('artifact.json') as f:
    artifact = json.load(f)

jsonschema.validate(instance=artifact, schema=schema)
print("Valid EDM v0.8 artifact")
```

---

## Schema Structure

EDM v0.8 defines **10 mandatory domains** (91 fields total, Full profile) plus the optional `extensions` domain:

### Representational Layer (57 fields)

- **CORE** (7 fields) - Narrative anchors: anchor, spark, wound, fuel, bridge, echo, narrative
- **CONSTELLATION** (19 fields) - Affective topology: emotions, narrative arcs, relational dynamics
- **MILKY_WAY** (5 fields) - Contextual framing: event type, location, people, tone shifts
- **GRAVITY** (14 fields) - Salience geometry: emotional weight, density, recall triggers
- **IMPULSE** (12 fields) - Motivational state: energy, drive, orientation, regulation

### Infrastructure Layer (34 fields)

- **META** (17 fields) - Identity & provenance: id, version, timestamps, consent, visibility
- **GOVERNANCE** (7 fields) - Rights & compliance: jurisdiction, retention, subject rights, k-anonymity
- **TELEMETRY** (4 fields) - Extraction metadata: model, confidence, extraction context
- **SYSTEM** (2 fields) - Compute boundary: embeddings, indices
- **CROSSWALKS** (4 fields) - Interoperability: Plutchik, Geneva Emotion Wheel, DSM-5, ISO mappings

[Complete Field Reference](docs/OVERVIEW.md)

---

## Significance Wiki Format

EDM artifacts can be rendered as a navigable markdown wiki using the [EDM Significance Wiki Format](docs/WIKI_FORMAT.md). The two-file pattern (`wiki_article.md` + `significance_article.md`) enables agents and individuals to build personal knowledge bases weighted by what mattered.

Reference implementation: [deepadata-edm-mcp-server](https://github.com/deepadata/deepadata-edm-mcp-server)

---

## Key Enum Values (v0.8)

Canonical values are preferred; free text is accepted where no canonical value
accurately represents the extracted content (two-tier enum model, v0.7.0+).

### emotion_primary
`joy`, `sadness`, `fear`, `anger`, `wonder`, `peace`, `tenderness`, `reverence`, `pride`, `anxiety`, `gratitude`, `longing`, `hope`, `shame`, `disappointment`, `relief`, `frustration`

### arc_type
`betrayal`, `liberation`, `grief`, `discovery`, `resistance`, `bond`, `moral_awakening`, `transformation`, `reconciliation`, `reckoning`, `threshold`, `exile`, `gratitude`, `authenticity`

### relational_dynamics
`parent_child`, `grandparent_grandchild`, `romantic_partnership`, `couple`, `sibling_bond`, `family`, `friendship`, `friend`, `companionship`, `colleague`, `mentorship`, `reunion`, `community_ritual`, `grief`, `self_reflection`, `professional`, `therapeutic`, `service`, `adversarial`

### narrative_archetype
`hero`, `caregiver`, `seeker`, `sage`, `lover`, `outlaw`, `innocent`, `magician`, `creator`, `everyman`, `jester`, `ruler`

The 12 canonical **identity** archetypes — which archetype the subject
embodies, not a story role (ADR-0030; `orphan` and `mentor` are excluded
as roles, not identities).

### tether_type
`person`, `symbol`, `event`, `place`, `ritual`, `object`, `tradition`, `identity`, `self`

### motivational_orientation
`belonging`, `safety`, `mastery`, `meaning`, `autonomy`, `authenticity`

---

## Compliance & Governance

EDM is designed for regulated environments:

| Regulation | EDM Support |
|------------|-------------|
| **EU AI Act** | Non-inferential representation; no behavioral prediction |
| **GDPR** | jurisdiction, consent_basis, subject_rights (portable, erasable, explainable) |
| **HIPAA** | policy_labels (health, biometrics), masking_rules, k_anonymity |
| **CCPA** | retention_policy, exportability controls |

The GOVERNANCE domain provides explicit fields for:
- Jurisdiction declaration (GDPR, CCPA, HIPAA, PIPEDA, LGPD)
- Retention policies (TTL, on_expiry actions)
- Subject rights (portable, erasable, explainable booleans)
- K-anonymity requirements
- Policy labels and masking rules

**See:** [EU AI Act Compliance Guide](docs/EU_AI_ACT_COMPLIANCE.md) for detailed regulatory mapping.

---

## Repository Structure

```
edm-spec/
├── schema/
│   ├── edm.v0.8.essential.schema.json # Essential profile (5 domains, 24 fields)
│   ├── edm.v0.8.extended.schema.json  # Extended profile (8 domains, 50 fields)
│   ├── edm.v0.8.full.schema.json      # Full profile (10 domains, 91 fields)
│   ├── fragments/                     # Shared domain schemas
│   │   ├── core.json
│   │   ├── constellation.json
│   │   ├── governance.json           # Compliance & rights
│   │   └── ... (11 total)
│   └── crosswalks/                   # Migration mappings
│       ├── v0.2_to_v0.3.json … v0.8.2_to_v0.8.3.json
├── examples/
│   ├── example-{essential,extended,full}-profile.json
│   └── example-partner-{journaling,therapy,companion,wiki}.json
├── test-vectors/                     # Canonical .ddna verification vectors
├── releases/                         # Versioned whitepaper documents
│   ├── v0.8.0/
│   ├── v0.8.1/
│   └── v0.8.3/
├── docs/
│   ├── OVERVIEW.md                   # Schema architecture
│   ├── PROFILES.md                   # Implementation & partner profiles
│   ├── CONFORMANCE.md                # Conformance levels
│   ├── SCOPE_AND_NONGOALS.md         # What EDM is and is not
│   ├── EDM_DDNA_BOUNDARY.md          # Transient vs persistent
│   ├── EU_AI_ACT_COMPLIANCE.md       # Regulatory compliance guide
│   ├── WIKI_FORMAT.md                # Significance Wiki two-file format
│   ├── VALIDATION.md                 # Validation guide
│   ├── RELEASE-NOTES.md
│   └── archive/                      # Historical migration guides
├── scripts/
│   └── validate-examples.mjs         # Validation utilities
├── CHANGELOG.md                      # Version history
├── CITATION.cff                      # Citation metadata
├── LICENSE                           # MIT License
├── SECURITY.md                       # Security policy
└── README.md
```

---

## Migration Guide

### v0.8.2 → v0.8.3 (July 2026)

Truth-only patch: the Full composite meta block gains `source_timestamp`
(conformance to the canonical fragment — widening only), field count
corrected to 91, `narrative_archetype` description corrected to the
identity definition. No migration required.
See `schema/crosswalks/v0.8.2_to_v0.8.3.json`.

### v0.8.1 → v0.8.2 (June 2026)

Fragment reconciliation to the canonical vocabulary: `narrative_archetype`
13 → 12 (`mentor` removed), `motivational_orientation` +`authenticity`,
`meta.profile` two-tier fragment fix, `meta.tags` spurious enum removed.
Migration needed only for artifacts carrying
`narrative_archetype = "mentor"`.
See `schema/crosswalks/v0.8.1_to_v0.8.2.json`.

### v0.8.0 → v0.8.1 (June 2026)

References and errata only. No structural change; no migration required.

### v0.7.0 → v0.8.0 (April 2026)

**New features:** Partner Profiles (§3.7.6), `meta.profile` two-tier model
(`partner:` prefix), arc_type +2 values, certification minimum bar.
See `schema/crosswalks/v0.7.0_to_v0.8.0.json`. No breaking changes.

### v0.6.0 → v0.7.0 (March 2026)

**New features:** Extensions domain, `arc_type` field, expanded enums, field deprecations.

See [RELEASE-NOTES.md](docs/RELEASE-NOTES.md) for full details.

### v0.5.1 → v0.6.0 (March 2026)

**Breaking change:** `meta.profile` is now required.

EDM v0.6.0 introduced Implementation Profiles. All artifacts must declare their profile:
- `"essential"` — Minimal footprint (24 fields)
- `"extended"` — Narrative depth (50 fields)
- `"full"` — Complete manifold (96 fields)

### v0.5.0 → v0.5.1 (March 2026)

Backwards-compatible enum additions. No breaking changes.

### v0.4.x → v0.5.0 (February 2026)

See [docs/archive/V05_MIGRATION_GUIDE.md](docs/archive/V05_MIGRATION_GUIDE.md) for full details.

### v0.3.x → v0.4.x

1. **Review changes:** 6 fields removed, GOVERNANCE domain added
2. **Migration guide:** [docs/archive/V04_MIGRATION_GUIDE.md](docs/archive/V04_MIGRATION_GUIDE.md)
3. **Use crosswalk:** `schema/crosswalks/v0.3_to_v0.4.json`
4. **Test thoroughly:** Validate migrated artifacts against v0.4 schema

---

## Contributing

We welcome contributions!

**Ways to contribute:**
- Open an [Issue](https://github.com/emotional-data-model/edm-spec/issues) for bugs or suggestions
- Submit a Pull Request for schema improvements
- Join [Discussions](https://github.com/emotional-data-model/edm-spec/discussions) for design questions
- Contact: jason@emotionaldatamodel.org

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Security issues:** Please report vulnerabilities privately via [SECURITY.md](SECURITY.md).

---

## Citation

If you use EDM in your research, please cite:

```bibtex
@software{harvey2026edm,
  author = {Harvey, Jason},
  title = {Emotional Data Model (EDM)},
  year = {2026},
  publisher = {Zenodo},
  version = {v0.8.3},
  doi = {10.5281/zenodo.17808652},
  url = {https://github.com/emotional-data-model/edm-spec}
}

```

*(10.5281/zenodo.17808652 is the concept DOI and resolves to the latest
published deposit; a version-specific v0.8.3 DOI will replace it once the
v0.8.3 Zenodo deposit is published.)*

---

## License

**MIT License** — See [LICENSE](LICENSE) file.

EDM is open source to enable proliferation and interoperability. The schema is free to use, modify, and distribute.

---

## About

EDM is maintained by DeepaData and the emotionaldatamodel.org standards body.

- **EDM** — Emotional Data Model (this specification)
- **.ddna** — Portable, signed emotional identity artifact
- **ESAA** — Emotional Safety Attestation Artifact

**Mission:** Make emotional AI safe, governed, and user-sovereign.

Website: [emotionaldatamodel.org](https://emotionaldatamodel.org) | [deepadata.com](https://deepadata.com)
GitHub: [@emotional-data-model](https://github.com/emotional-data-model)
Contact: jason@emotionaldatamodel.org

---

## Links

- **Whitepaper (latest published deposit, v0.8.1):** [Zenodo Record](https://doi.org/10.5281/zenodo.20678017)
- **Concept DOI (all versions):** [10.5281/zenodo.17808652](https://doi.org/10.5281/zenodo.17808652)
- *Note:* The v0.8.0 deposit (10.5281/zenodo.19555166) exists outside the main version chain, cross-linked via related identifiers. v0.8.1 reunifies the lineage under concept 17808652. v0.8.2 was npm-only (no deposit); the v0.8.3 deposit is pending.
- **Repository:** https://github.com/emotional-data-model/edm-spec
- **Issues:** https://github.com/emotional-data-model/edm-spec/issues

---

**Last Updated:** July 2026
**Version:** 0.8.3
**License:** MIT
