# EDM Scope and Non-Goals

**Version:** 1.0
**Last Updated:** January 2026
**Status:** Normative guidance for EDM v0.6.0

---

## Purpose

This document establishes clear boundaries around what the Emotional Data Model (EDM) is and what it is not. As EDM transitions to public availability, precise scope definition prevents misinterpretation, misuse, and misaligned expectations.

EDM is a specification. This document is normative guidance for understanding that specification.

---

## What EDM Is

### A Governance-First Representational Schema

EDM is a JSON Schema specification that defines how emotional context should be structured, validated, and governed. It provides a canonical format for representing affective data in AI systems.

**Architectural classification:** EDM operates at the **representation layer**. It defines data structure and semantics. It does not define persistence mechanisms, computation logic, or runtime behavior.

### Profile-Conditional Structure

EDM v0.6.0 defines **profile-conditional domain sets**: Essential (25 fields), Extended (50 fields), Full (96 fields across all 10 domains):

| Layer | Domains | Field Count | Purpose |
|-------|---------|-------------|---------|
| **Representational** | CORE, CONSTELLATION, MILKY_WAY, GRAVITY, IMPULSE | 57 | Encode emotional content |
| **Infrastructure** | META, GOVERNANCE, TELEMETRY, SYSTEM, CROSSWALKS | 39 | Enable governance and interoperability |

An artifact contains only the domains defined for its declared profile. See PROFILES.md Section 3.7 for exact domain sets per profile. This ensures:
- Predictable validation
- Consistent tooling interfaces
- Explicit handling of unknown values

### Transient by Default

EDM artifacts are designed for **session-scoped** use with a default retention expectation of **24 hours or less**. This transience is a security and privacy feature:

- Emotional data should not persist indefinitely without explicit commitment
- Short retention windows limit exposure risk
- Users must take explicit action (sealing into .ddna) to persist emotional identity

Transience is a design principle, not a technical enforcement. Implementations must honor retention policies declared in the GOVERNANCE domain.

**Note:** Mechanisms for enforcing session boundaries and retention limits are implementation-specific and outside the scope of this specification. This is a normative design principle, not a technical enforcement mandate.

### Non-Inferential Representation

**This is a structural invariant of EDM.**

Every field in the EDM schema must contain only:
- **Extracted content** — derived from explicit user-provided material
- **Declared content** — explicitly stated by the user

No field may contain:
- Psychological inference beyond the provided content
- Behavioral predictions
- Diagnostic assessments
- Biometric analysis results

This constraint is not merely a policy recommendation. It is a definitional boundary of what constitutes valid EDM data.

### Compliance Infrastructure

EDM provides fields for regulatory compliance but does not interpret or enforce law:

| Domain | Compliance Function |
|--------|---------------------|
| **META** | Consent basis, PII classification, provenance |
| **GOVERNANCE** | Jurisdiction, retention, subject rights, k-anonymity, masking |
| **TELEMETRY** | Extraction audit trail |

These fields enable compliance; they do not certify it. Organizations remain responsible for legal interpretation and enforcement.

---

## What EDM Is Not

### Not an Emotion Recognition System

EDM does not detect, infer, or recognize emotions. It provides a schema for representing emotional context that has been **explicitly provided or extracted from user content**.

| EDM Does | EDM Does Not |
|----------|--------------|
| Define fields for emotional states | Analyze facial expressions |
| Accept declared emotional context | Process voice for mood detection |
| Structure extracted narrative content | Interpret biometric signals |
| Validate emotional data format | Score emotional intensity algorithmically |

**Why this matters:** The EU AI Act prohibits emotional recognition from biometrics in workplace and educational contexts. EDM's non-inferential architecture ensures it operates outside this prohibition by design.

### Not a Biometric Inference Engine

EDM explicitly excludes biometric emotion inference **within EDM-native fields**:

- No fields for facial expression analysis
- No fields for voice sentiment detection
- No fields for physiological signal interpretation
- No fields for behavioral pattern prediction

The `meta.source_type` field accepts `text`, `audio`, `image`, `video`, and `mixed`, but these refer to the **medium of user-provided content**, not the subject of biometric analysis.

**Example:** An audio source type means emotional context was extracted from what the user said (speech content), not from how they said it (vocal biomarkers).

**Crosswalk interoperability:** EDM may reference external affective or biometric systems via the CROSSWALKS domain, but such systems operate outside the EDM representational boundary. External system outputs must not be written into EDM fields unless they meet the non-inferential interpretation criteria defined in this document.

### Not a Memory Store

EDM defines the **shape** of emotional data. It does not store, index, retrieve, or manage that data.

| EDM Provides | External Systems Provide |
|--------------|--------------------------|
| Schema for emotional artifacts | Storage backends |
| Validation rules | Indexing and retrieval |
| Governance field structure | Query interfaces |
| Interoperability format | Persistence guarantees |

Memory systems (vector databases, document stores) may store EDM-conformant JSON artifacts. However, **storage of an EDM artifact outside a .ddna envelope does not constitute a certified, sovereign, or compliance-grade emotional record.**

Raw JSON EDM artifacts are informational; .ddna-sealed artifacts are authoritative. Only .ddna envelopes provide cryptographic integrity, identity binding, and governance enforcement guarantees.

EDM itself is not a memory layer.

### Not an Identity Provider

EDM does not authenticate users or establish identity:

- `meta.owner_user_id` references an external identity; it does not create one
- Authentication remains the responsibility of external identity providers
- EDM provides no identity verification mechanisms

The planned VitaPass system will provide cross-vendor identity for emotional data, but this is external to the EDM specification.

### Not a Certificate Authority

EDM does not issue certificates or establish trust hierarchies:

- The .ddna signing model provides **integrity verification**, not trust authority
- Verification proves "this data was signed by this key" — not "this signer is trustworthy"
- Trust decisions belong to consuming systems

EDM is not a PKI. It does not define certificate chains, revocation lists, or trust anchors.

### Not a Regulator

EDM provides compliance infrastructure but does not:

- Interpret law
- Certify compliance
- Replace legal counsel
- Audit implementations

The GOVERNANCE domain enables organizations to declare and enforce their compliance posture. EDM does not validate the correctness of those declarations.

### Not a Psychological Assessment Tool

EDM is not designed for clinical use:

- No diagnostic fields
- No assessment scoring
- No clinical terminology requirements
- No therapeutic protocol integration

While EDM may be used in healthcare contexts (with appropriate `governance.policy_labels`), it is not a psychological instrument and must not be positioned as one.

### Not a Replacement for Existing Systems

EDM complements, rather than replaces, existing infrastructure:

| System | Relationship to EDM |
|--------|---------------------|
| **Mem0** | EDM provides governed format for emotional memories stored in Mem0 |
| **MCP** | EDM artifacts can be exposed as MCP Resources |
| **A2A** | EDM provides emotional context payload for agent communication |
| **Vector databases** | EDM artifacts can be embedded and retrieved |
| **LLM providers** | EDM provides structured emotional context for any provider |

EDM is a **governance layer**, not a competing system.

---

## The Interpretation vs Inference Boundary

This distinction is fundamental to EDM's compliance posture and must be clearly understood.

### What Is Permitted: Interpretation

**Interpretation** derives meaning from content the user has explicitly provided. It operates within the semantic scope of the source material.

| Permitted Interpretation | Example |
|--------------------------|---------|
| Extracting emotional themes from narrative | User writes "I felt overwhelmed by grief" → `constellation.emotion_primary: "sadness"` |
| Identifying symbolic meaning in described objects | User describes grandmother's rocking chair → `constellation.symbolic_anchor: "rocking chair"` |
| Recognizing relational context from described relationships | User mentions "my late father" → `constellation.relational_dynamics: "grief"` |
| Classifying narrative arc from story structure | User describes journey from loss to acceptance → `constellation.narrative_arc: "transformation"` |

Interpretation is **bounded by the source content**. It does not extend beyond what the user has provided.

### What Is Prohibited: Inference

**Inference** derives conclusions beyond the provided content, typically by applying psychological models, behavioral analysis, or predictive algorithms.

| Prohibited Inference | Why Prohibited |
|----------------------|----------------|
| Diagnosing depression from word choice patterns | Psychological diagnosis beyond content |
| Predicting future emotional states | Behavioral prediction |
| Detecting deception from linguistic markers | Psychological assessment |
| Inferring personality type from writing style | Latent psychological reconstruction |
| Identifying emotional disorders from response patterns | Clinical inference without explicit basis |

**Important:** Inference may exist in external systems and processes. The prohibition applies to **representing inferred results as EDM data**, not to performing analysis outside EDM's representational boundary. Organizations may use proprietary models or inference engines; such outputs simply cannot be written into EDM fields unless explicitly declared by the user.

### The Operational Test

When populating an EDM field, apply this test:

1. **Is this content explicitly stated or directly described in the source material?**
   - If yes → Permitted (extraction)

2. **Is this content a reasonable interpretation of explicitly described narrative, symbols, or relationships?**
   - If yes → Permitted (interpretation)

3. **Does this content require psychological theory, behavioral models, or predictive analysis beyond the source material?**
   - If yes → **Prohibited** (inference)

### Example: The Boundary in Practice

**User input:** "I've been visiting my grandmother's empty house every Sunday since she passed. I sit in her rocking chair and remember her laugh."

| Field | Permitted Value | Prohibited Value |
|-------|-----------------|------------------|
| `core.anchor` | "grandmother" | *(same)* |
| `core.echo` | "her laugh" | *(same)* |
| `constellation.emotion_primary` | "tenderness" or "sadness" | "depression" (diagnostic) |
| `constellation.symbolic_anchor` | "rocking chair" | *(same)* |
| `constellation.relational_dynamics` | "grief" | *(same)* |
| `gravity.recurrence_pattern` | "cyclical" | *(same)* |
| `impulse.attachment_style` | null (not stated) | "anxious" (inferred) |

The `attachment_style` field must be null unless the user explicitly describes their attachment pattern. Inferring it from behavior is prohibited.

---

## Tooling Is Non-Normative

### The Canonical Source of Truth

The JSON Schema file `schema/edm.v0.6.schema.json` is the sole normative definition of EDM.

- All validation MUST use this schema or a conformant implementation
- Documentation, examples, and tooling are informative
- Conflicts between tooling behavior and schema definition resolve in favor of the schema

**Note:** Schema validation confirms structural conformance only. It does not certify trust, sovereignty, or compliance. Certification is a policy-layer concern handled by .ddna envelope signing and verification, not by schema validation alone.

### Reference Implementations

All tooling produced by DeepaData is **reference implementation only**:

| Tooling | Status | Implication |
|---------|--------|-------------|
| Validators | Reference | Any conformant validator may replace |
| SDKs | Reference | Any conformant SDK may replace |
| CLI tools | Reference | Any conformant CLI may replace |
| MCP servers | Reference | Any conformant server may replace |

Third parties implementing EDM tooling need not use DeepaData code. They need only conform to the schema.

### Why This Matters

Non-normative tooling ensures:

1. **No vendor lock-in** — The specification is open; implementations are replaceable
2. **Innovation freedom** — Better tooling can emerge without specification changes
3. **Clear accountability** — Bugs in tooling are implementation issues, not specification defects
4. **Ecosystem health** — Multiple implementations validate the specification's clarity

---

## Common Misinterpretations

### "EDM is an emotion AI product"

**Incorrect.** EDM is a specification, not a product. It defines data format and governance structure. Products may be built using EDM, but EDM itself is not a product.

### "EDM competes with memory systems"

**Incorrect.** EDM complements existing memory infrastructure. Memory systems provide storage and retrieval; EDM provides governed format for emotional data within those systems. They operate at different layers.

### "EDM can detect how users feel"

**Incorrect.** EDM cannot detect anything. It provides a schema for representing emotional context that users declare or that is extracted from user-provided content. Detection and inference are explicitly prohibited.

### "EDM artifacts should be stored permanently"

**Incorrect.** EDM artifacts are transient by design (24h default). Permanent storage requires explicit commitment via .ddna sealing. Implementations storing EDM artifacts beyond session scope must honor GOVERNANCE retention policies.

### "EDM replaces consent mechanisms"

**Incorrect.** EDM provides fields for documenting consent (`meta.consent_basis`, `meta.consent_scope`). It does not collect, verify, or enforce consent. Consent mechanisms remain the responsibility of implementing systems.

### "EDM tooling is required to use EDM"

**Incorrect.** Any system capable of producing and validating JSON conformant to the EDM schema can use EDM. DeepaData tooling is reference implementation for convenience, not requirement.

### "EDM fields can be populated by AI analysis"

**Partially incorrect.** EDM fields can be populated by AI extraction from user-provided content (interpretation). They cannot be populated by AI inference beyond that content. The AI must operate within the interpretation boundary defined above.

---

## Summary

| Aspect | EDM Is | EDM Is Not |
|--------|--------|------------|
| **Type** | Specification | Product |
| **Layer** | Representation | Persistence, Computation |
| **Scope** | Emotional data format | Emotion detection |
| **Inference** | Interpretation only | Psychological inference |
| **Tooling** | Non-normative reference | Required implementation |
| **Compliance** | Infrastructure | Certification |
| **Identity** | Format for identity data | Identity provider |
| **Memory** | Format for memory systems | Memory system |

EDM defines how emotional data should be structured and governed. Everything else is outside its scope.

---

## Related Documents

- [EDM and .ddna Boundary](EDM_DDNA_BOUNDARY.md) — Transient vs persistent artifacts
- [EU AI Act Compliance](EU_AI_ACT_COMPLIANCE.md) — Regulatory mapping
- [Overview](OVERVIEW.md) — Schema architecture

---

**Normative Reference:** `schema/edm.v0.6.schema.json`
**Contact:** jason@deepadata.com
**Repository:** https://github.com/deepadata/deepadata-edm-spec
