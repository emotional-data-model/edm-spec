# EDM and .ddna Boundary

**Version:** 1.0
**Last Updated:** March 2026
**Status:** Normative guidance for EDM v0.6.0

---

## Purpose

This document establishes the architectural boundary between EDM (transient emotional representation) and .ddna (persistent emotional identity). Clear separation of these concepts is essential for:

- Correct implementation of emotional data systems
- Appropriate privacy and governance posture
- Regulatory compliance (particularly regarding data retention)
- User sovereignty over emotional identity

EDM and .ddna are complementary but distinct. This document defines that distinction.

---

## The Core Distinction

**EDM describes data. .ddna describes a subject.**

An EDM artifact captures emotional context from a specific interaction or session. It is structured, validated, and governed—but fundamentally transient.

A .ddna artifact commits emotional identity to persistent form. It wraps EDM content in a cryptographically-signed envelope that provides integrity, provenance, and portability guarantees.

| Aspect | EDM | .ddna |
|--------|-----|-------|
| **Primary Purpose** | Represent emotional context | Preserve emotional identity |
| **Temporal Scope** | Session (24h default) | Persistent (user-controlled) |
| **Mutability** | Editable | Sealed (immutable payload) |
| **Integrity Model** | Schema validation | Cryptographic signature |
| **Identity Binding** | Optional (`owner_user_id`) | Required (subject commitment) |
| **Governance** | Declared (fields present) | Inherited + enforced |
| **Portability** | Format-portable | Integrity-portable |
| **Commitment Level** | Draft / working state | Final / committed state |

---

## Architectural Layering

EDM and .ddna operate at different architectural layers. Understanding this layering prevents confusion about responsibilities and capabilities.

### Layer 1: Representation (EDM)

**Function:** Define the structure and semantics of emotional data.

EDM operates purely at the representation layer. It specifies:

- What fields exist and what they mean
- How fields are validated
- What governance metadata must accompany emotional content
- How emotional data interoperates with external taxonomies

**EDM does not specify:**
- How data is stored
- How data is transmitted
- How signatures are computed
- How identity is verified

**Artifacts at this layer:** `.edm.json` files (transient, editable, session-scoped)

### Layer 2: Persistence (.ddna)

**Function:** Commit emotional representation to durable, portable, tamper-evident form.

The .ddna layer wraps EDM content and adds:

- Cryptographic signature over canonical payload
- Envelope metadata (signing key, timestamp, algorithm)
- Audit chain for provenance tracking
- Integrity guarantees for cross-system portability

**The .ddna layer depends on EDM but extends it.** A .ddna artifact contains a valid EDM payload; the EDM payload does not know about .ddna.

**Artifacts at this layer:** `.ddna.json` files (persistent, sealed, identity-scoped)

### Layer 3: Computation (External Systems)

**Function:** Process, analyze, retrieve, and act upon emotional data.

Computation is explicitly outside EDM and .ddna scope:

- Memory systems (Mem0, vector databases)
- Agent runtimes (MCP servers, A2A communication)
- Retrieval algorithms (embedding, search, ranking)
- Application logic (chatbots, companions, therapeutic tools)

**EDM and .ddna provide data to computational systems. They do not perform computation.**

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 3: COMPUTATION                         │
│                    (External Systems)                           │
│                                                                 │
│  Memory Systems    Agent Runtimes    Retrieval    Applications  │
│  (Mem0, Vector)    (MCP, A2A)        Algorithms   (Chatbots)    │
│                                                                 │
│  ───────────────────────────────────────────────────────────────│
│                         ▲                                       │
│                         │ consumes                              │
│                         │                                       │
├─────────────────────────┼───────────────────────────────────────┤
│                    LAYER 2: PERSISTENCE                         │
│                    (.ddna)                                      │
│                                                                 │
│  Cryptographic Signing    Envelope Metadata    Audit Chain      │
│  Integrity Guarantees     Portability          Provenance       │
│                                                                 │
│  ───────────────────────────────────────────────────────────────│
│                         ▲                                       │
│                         │ seals                                 │
│                         │                                       │
├─────────────────────────┼───────────────────────────────────────┤
│                    LAYER 1: REPRESENTATION                      │
│                    (EDM)                                        │
│                                                                 │
│  5–10 Domains    24–96 Fields    Schema Validation    Governance │
│  Non-Inferential           Transient by Default                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## EDM: Transient Emotional Context

### Definition

An EDM artifact is a JSON object conforming to the EDM v0.4 schema. It represents emotional context extracted from or declared in a specific interaction.

### Characteristics

**Structural completeness:** Domains present are determined by the declared profile: Essential (5), Extended (8), Full (10)

**Schema validation:** Validity is determined by conformance to the profile-specific schema (e.g., `schema/edm.v0.6.full.schema.json`). No cryptographic verification.

**Mutability:** EDM artifacts can be freely edited, enriched, or corrected. There is no integrity seal.

**Transience:** Default retention is 24 hours or less. Extended retention requires explicit governance declaration or .ddna commitment.

**Optional identity:** The `meta.owner_user_id` field is optional. EDM artifacts can exist in stateless mode with no identity binding.

### Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Content    │     │  Extraction  │     │     EDM      │
│   Provided   │ ──► │  (SDK/Manual)│ ──► │   Artifact   │
│              │     │              │     │  (transient) │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 │ session ends
                                                 ▼
                                          ┌──────────────┐
                                          │   Expired/   │
                                          │   Deleted    │
                                          └──────────────┘
```

### Use Cases

| Use Case | Why EDM (not .ddna) |
|----------|---------------------|
| Real-time session context | No commitment needed; data is ephemeral |
| Draft emotional profile | User reviewing before commitment |
| Temporary AI memory | Short-term coherence, not long-term identity |
| Testing and development | Iteration without persistence overhead |
| Privacy-sensitive contexts | Minimizing retained emotional data |

### Example EDM Artifact (Truncated)

```json
{
  "meta": {
    "id": null,
    "version": "0.6.0",
    "profile": "essential",
    "created_at": "2026-01-14T10:30:00Z",
    "owner_user_id": null,
    "visibility": "private",
    "pii_tier": "moderate",
    "source_type": "text",
    "consent_basis": "consent"
  },
  "core": {
    "anchor": "childhood home",
    "spark": "finding old photographs",
    "narrative": "User described returning to childhood home..."
  },
  "constellation": {
    "emotion_primary": "tenderness",
    "narrative_arc": "reflection"
  },
  "governance": {
    "jurisdiction": "GDPR",
    "retention_policy": {
      "ttl_days": 1,
      "on_expiry": "hard_delete"
    }
  }
}
```

This artifact has no `meta.id`, no `owner_user_id`, and a 1-day TTL. It is purely transient.

---

## .ddna: Persistent Emotional Identity

### Definition

A .ddna artifact is a sealed envelope containing:
1. A valid EDM payload (frozen at sealing time)
2. A cryptographic signature over the canonical payload
3. Envelope metadata (signing key reference, algorithm, timestamp)
4. Audit chain entries (for provenance tracking)

### Characteristics

**Immutable payload:** Once sealed, the EDM content cannot be modified without invalidating the signature.

**Cryptographic integrity:** Verification confirms the payload has not been tampered with since signing.

**Required identity:** .ddna artifacts represent committed emotional identity. Subject binding is required.

**Persistent:** .ddna artifacts are designed for long-term storage and cross-system portability.

**Provenance chain:** Audit entries track the artifact's history (creation, transfers, access).

### What Sealing Provides

| Guarantee | Mechanism |
|-----------|-----------|
| **Integrity** | Signature over canonical bytes; tampering is detectable |
| **Provenance** | Signature traces to specific key at specific time |
| **Portability** | Self-contained artifact can move between systems |
| **Non-repudiation** | Signer cannot deny having signed (given key security) |
| **Auditability** | Audit chain provides access and transfer history |

### What Sealing Does NOT Provide

| NOT Provided | Explanation |
|--------------|-------------|
| **Trust** | Signature proves integrity, not trustworthiness of signer |
| **Accuracy** | Sealed content may still be incorrect; sealing doesn't validate truth |
| **Authorization** | Sealing doesn't grant access rights to the content |
| **Compliance certification** | Governance fields are inherited, not certified |
| **Identity authentication** | Subject identity must be established externally |

### Why Raw JSON Cannot Provide These Guarantees

Understanding why .ddna is necessary requires understanding what raw JSON EDM artifacts fundamentally cannot provide:

| Guarantee | .ddna Mechanism | Why Raw JSON Fails |
|-----------|-----------------|-------------------|
| **Integrity** | Signature over canonical bytes | Raw JSON has no signature; tampering is silent and undetectable |
| **Provenance** | Signing key + timestamp binding | Raw JSON has no cryptographic binding to any key or moment |
| **Non-repudiation** | Signer cannot deny signature | Raw JSON can be created by anyone; no authorship proof exists |
| **Tamper detection** | Signature invalidation | Raw JSON can be modified without any indication of change |
| **Auditability** | Audit chain entries | Raw JSON has no built-in history mechanism |

**The fundamental difference:** Raw JSON is just data. Anyone can create, copy, or modify it. There is no way to verify that a raw JSON EDM artifact:
- Was created by any particular party
- Has not been modified since creation
- Represents a committed identity record

**.ddna sealing adds cryptography.** Cryptographic signatures provide mathematical proof of integrity and provenance. Without sealing, EDM artifacts are informational drafts—useful for session context, but not authoritative records.

**Implication for implementers:** If your use case requires any of the five guarantees listed above, raw JSON storage is insufficient. You must seal artifacts into .ddna envelopes.

### Lifecycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│     EDM      │     │   Sealing    │     │    .ddna     │
│   Artifact   │ ──► │  (ddna-tools)│ ──► │   Artifact   │
│  (transient) │     │              │     │ (persistent) │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                            ┌────────────────────┼────────────────────┐
                            │                    │                    │
                            ▼                    ▼                    ▼
                     ┌────────────┐       ┌────────────┐       ┌────────────┐
                     │  Storage   │       │  Transfer  │       │   Export   │
                     │ (archive)  │       │ (portable) │       │ (user)     │
                     └────────────┘       └────────────┘       └────────────┘
```

### Use Cases

| Use Case | Why .ddna (not EDM) |
|----------|---------------------|
| Cross-platform identity portability | Integrity must survive system transfers |
| Long-term emotional archive | Persistence beyond session scope |
| Compliance audit trail | Tamper-evident record required |
| User data export | Verifiable, portable format for user sovereignty |
| Therapeutic continuity | Emotional history preserved across providers |

---

## The Commitment Event: Sealing

Sealing is the commitment event that transforms transient EDM into persistent .ddna.

### Prerequisites for Sealing

1. **Valid EDM artifact:** Payload must pass schema validation
2. **Identity binding:** `meta.owner_user_id` should be populated (or explicit stateless declaration)
3. **Governance completeness:** `governance` domain should reflect intended retention and rights
4. **User consent:** Sealing represents user commitment; consent should be explicit

### Sealing Process

```
┌─────────────────────────────────────────────────────────────────┐
│                        SEALING PROCESS                          │
│                                                                 │
│  1. VALIDATION                                                  │
│     └─► Verify EDM artifact against schema                      │
│     └─► Check required fields present                           │
│     └─► Validate governance completeness                        │
│                                                                 │
│  2. CANONICALIZATION                                            │
│     └─► Apply deterministic JSON serialization (RFC 8785 JCS)   │
│     └─► Produce byte-stable payload                             │
│                                                                 │
│  3. SIGNING                                                     │
│     └─► Compute signature over canonical bytes                  │
│     └─► Use specified algorithm (e.g., Ed25519)                 │
│     └─► Record signing key reference and timestamp              │
│                                                                 │
│  4. ENVELOPE ASSEMBLY                                           │
│     └─► Package: payload + signature + metadata                 │
│     └─► Initialize audit chain                                  │
│     └─► Output: .ddna artifact                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Post-Sealing State

After sealing:
- The EDM payload is **frozen** — modifications invalidate the signature
- The artifact is **portable** — can move between systems with integrity intact
- The artifact is **auditable** — provenance can be verified
- The artifact is **persistent** — intended for long-term retention

### Unsealing (Verification)

Verification confirms integrity but does not "unseal" in the sense of making the payload editable:

```
┌─────────────────────────────────────────────────────────────────┐
│                      VERIFICATION PROCESS                       │
│                                                                 │
│  1. EXTRACT                                                     │
│     └─► Parse envelope structure                                │
│     └─► Retrieve payload, signature, metadata                   │
│                                                                 │
│  2. CANONICALIZE                                                │
│     └─► Apply same canonicalization to extracted payload        │
│     └─► Produce byte-stable representation                      │
│                                                                 │
│  3. VERIFY                                                      │
│     └─► Check signature against canonical bytes                 │
│     └─► Verify signing key is valid                             │
│     └─► Report: VALID or INVALID (with reason)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Decision Guide: EDM vs .ddna

Use this decision tree to determine when to use EDM only vs when to create a .ddna artifact.

### Use EDM Only When:

- [ ] Data is session-scoped and will not persist beyond the interaction
- [ ] User has not committed to long-term storage
- [ ] System operates in stateless mode (no identity binding)
- [ ] Data is draft/working state subject to revision
- [ ] Privacy requirements demand minimal retention
- [ ] Testing or development context

### Create .ddna When:

- [ ] User explicitly commits to persisting their emotional identity
- [ ] Data must transfer between systems with integrity
- [ ] Compliance requires tamper-evident audit trail
- [ ] Long-term archival is the intended use case
- [ ] User requests data export in portable format
- [ ] Cross-vendor identity portability is required

### Decision Flowchart

```
                    ┌─────────────────────┐
                    │  Emotional context  │
                    │     captured        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Does user want to  │
                    │  persist this data? │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │ No             │                │ Yes
              ▼                │                ▼
    ┌─────────────────┐        │      ┌─────────────────┐
    │  Retain as EDM  │        │      │  Is integrity   │
    │  (honor TTL)    │        │      │  required?      │
    └─────────────────┘        │      └────────┬────────┘
                               │               │
                               │    ┌──────────┼──────────┐
                               │    │ No       │          │ Yes
                               │    ▼          │          ▼
                               │  ┌────────────┴───┐  ┌─────────────┐
                               │  │ Store EDM with │  │ Seal as     │
                               │  │ extended TTL   │  │ .ddna       │
                               │  └────────────────┘  └─────────────┘
```

---

## Stateless Artifacts and Identity Binding

### Stateless Mode

EDM supports **stateless mode** where artifacts have no identity binding:

- `meta.owner_user_id` is null
- `meta.id` may be null
- No persistence expectation
- Pure session context

Stateless artifacts cannot be meaningfully sealed into .ddna because there is no subject to bind.

### Identity Binding Requirements for .ddna

To seal an EDM artifact into .ddna:

1. **Subject must be identifiable:** `meta.owner_user_id` should reference a resolvable identity
2. **Consent must be documented:** `meta.consent_basis` must reflect user agreement
3. **Governance must be complete:** The `governance` domain must accurately reflect intended handling

### Stateless vs Stateful Summary

| Aspect | Stateless EDM | Stateful EDM | .ddna |
|--------|---------------|--------------|-------|
| `owner_user_id` | null | populated | required |
| `meta.id` | optional | recommended | required |
| Persistence | none | session | permanent |
| Sealable | no | yes | n/a (already sealed) |
| Use case | Anonymous context | User session | Identity archive |

---

## Governance Inheritance

When EDM is sealed into .ddna, governance fields are **inherited and locked**:

| Field | Behavior After Sealing |
|-------|------------------------|
| `governance.jurisdiction` | Locked; cannot be changed |
| `governance.retention_policy` | Locked; defines .ddna retention |
| `governance.subject_rights` | Locked; portable/erasable/explainable frozen |
| `governance.exportability` | Locked; controls .ddna export |
| `meta.consent_basis` | Locked; legal basis preserved |

**Implication:** Governance posture must be correct before sealing. Post-sealing changes require creating a new .ddna artifact.

---

## File Extension Conventions

| Extension | Meaning | Status |
|-----------|---------|--------|
| `.edm.json` | Transient EDM artifact (unsealed) | Recommended for clarity |
| `.ddna.json` | Sealed .ddna artifact | Standard |
| `.json` | Ambiguous; context-dependent | Avoid for production |

**Recommendation:** Use `.edm.json` for unsealed artifacts and `.ddna.json` for sealed artifacts. This convention clarifies persistence expectations and prevents accidental treatment of transient data as certified records.

**Note:** Example files in this repository may use `.ddna.json` for demonstration purposes.

---

## Summary

| Question | EDM Answer | .ddna Answer |
|----------|------------|--------------|
| What does it represent? | Emotional context | Emotional identity |
| How long does it last? | Session (24h default) | Permanent (user-controlled) |
| Can it be edited? | Yes | No (invalidates signature) |
| Is it signed? | No | Yes |
| Does it require identity? | No | Yes |
| Is it portable? | Format-portable | Integrity-portable |
| When is it used? | During interaction | After commitment |

**The boundary is commitment.** EDM is working state. .ddna is committed state. Sealing is the commitment event.

---

## Related Documents

- [Scope and Non-Goals](SCOPE_AND_NONGOALS.md) — What EDM is and is not
- .ddna Signing Model — Cryptographic design (specification in progress)
- [EU AI Act Compliance](EU_AI_ACT_COMPLIANCE.md) — Regulatory mapping
- [Overview](OVERVIEW.md) — Schema architecture

---

**Normative References:** `schema/edm.v0.6.{essential,extended,full}.schema.json`
**Contact:** jason@emotionaldatamodel.org
**Repository:** https://github.com/emotional-data-model/edm-spec
