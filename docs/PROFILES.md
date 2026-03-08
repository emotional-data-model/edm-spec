# EDM v0.6.0 — Implementation Profiles

## 3.7.1 Overview

EDM defines three implementation profiles that specify the minimum required fields for a conforming artifact. Profiles enable graduated adoption: memory platforms and agent frameworks may implement the lightweight Core Profile, while regulated therapeutic applications require the Full Profile.

**Profiles are orthogonal to conformance levels (Section 3.8).** A profile defines WHAT is extracted — the depth of emotional representation. A conformance level defines HOW an artifact is governed — the trust and verification posture. Any profile may achieve any conformance level for which it is eligible.

## 3.7.2 Profile Declarations

A conforming artifact MUST declare its profile in the `meta.profile` field. Valid values are:

| Value | Profile |
|-------|---------|
| `"core"` | Core Profile |
| `"extended"` | Extended Profile |
| `"full"` | Full Profile |

The `meta.profile` field MUST be present and MUST contain one of the above values. Omission of this field renders the artifact non-conforming to EDM v0.6.0 and later.

## 3.7.3 Core Profile

The Core Profile (~20 required fields) defines the minimum viable artifact for session coherence and real-time retrieval. It is designed for memory platforms, agent frameworks, and AI assistants that require affective context without therapeutic depth.

### Required Domains and Fields

**Meta Domain** (8 fields):
- `id` — artifact identifier (required)
- `version` — EDM version string (required)
- `profile` — profile declaration (required; value: `"core"`)
- `created_at` — ISO-8601 timestamp (required)
- `owner_user_id` — subject identifier (required)
- `consent_basis` — legal basis for processing (required)
- `visibility` — access control level (required)
- `pii_tier` — data sensitivity classification (required)

**Core Domain** (7 fields — all required):
- `anchor`, `spark`, `wound`, `fuel`, `bridge`, `echo`, `narrative`

**Constellation Domain** (3 fields required; remainder null):
- `emotion_primary` — primary emotional classification (required)
- `emotion_subtone` — array of supporting tones (required; may be empty)
- `narrative_arc` — narrative structure (required)
- All other Constellation fields MUST be explicitly null

**Governance Domain** (minimum required):
- `jurisdiction` — applicable legal regime (required)
- `retention_policy.basis` — retention justification (required)
- `retention_policy.ttl_days` — retention period (required)
- `retention_policy.on_expiry` — expiry action (required)
- `subject_rights.portable` — portability flag (required)
- `subject_rights.erasable` — erasability flag (required)
- `subject_rights.explainable` — explainability flag (required)

**Telemetry Domain** (structural presence required):
- All fields may be null but the domain MUST be present

**Milky_Way, Gravity, Impulse, System, Crosswalks Domains**:
- Structural presence required
- All fields MUST be explicitly null

### Core Profile Use Cases

- Companion AI session context
- Memory compression and summarisation
- Stateless session coherence
- Agent framework emotional grounding

## 3.7.4 Extended Profile

The Extended Profile (~45 required fields) provides full narrative and emotional topology without the complete salience geometry of the Full Profile. It is designed for journaling applications, companion AI with longitudinal context, and workplace wellness platforms.

### Required Domains and Fields

The Extended Profile includes all Core Profile requirements, plus:

**Constellation Domain** (all fields required):
- Full population of all 18 Constellation fields

**Milky_Way Domain** (key fields required):
- `event_type` — event classification (required)
- `location_context` — spatial context (required)
- `associated_people` — array of related persons (required; may be empty)
- `visibility_context` — sharing scope (required)
- `tone_shift` — tonal transition (may be null)

**Gravity Domain** (key fields required):
- `emotional_weight` — salience score 0.0–1.0 (required)
- `valence` — affective polarity (required)
- `tether_type` — attachment classification (required)
- `recurrence_pattern` — temporal pattern (required)
- `strength_score` — retrieval strength 0.0–1.0 (required)
- Other Gravity fields may be null

**Impulse Domain**:
- Structural presence required
- All fields may be null

### Extended Profile Use Cases

- Journaling and reflective writing applications
- Companion AI with longitudinal memory
- Workplace wellness and coaching platforms
- Therapy session capture (non-clinical)

## 3.7.5 Full Profile

The Full Profile (96 fields) provides the complete representational manifold across all ten domains. It is required for regulated contexts, enterprise compliance, and VitaPass issuance.

### Required Domains and Fields

All ten domains MUST be fully populated. No field may be null unless the source content genuinely provides no basis for extraction. The extraction system MUST attempt population of all fields.

### Full Profile Use Cases

- Regulated therapy platforms
- Clinical documentation
- EU AI Act Article 5(1)(f) compliance documentation
- Enterprise audit and compliance
- VitaPass longitudinal registry entry (Full + Certified, future capability)
- DeepaData Certified conformance (see Section 3.8)

Note: VitaPass binding — cross-vendor portability of sealed artifacts — is available at Sealed conformance for all profiles, not Full only. Full Profile is required only for the longitudinal registry layer.

## 3.7.6 Profile Invariants

The following invariants apply to all profiles:

1. **Domain Completeness**: All ten domains MUST be structurally present in every artifact, regardless of profile. An artifact missing any domain is non-conforming.

2. **Explicit Null Requirement**: Fields not required by a profile MUST be set to explicit `null` values. Field omission is prohibited. This preserves schema stability and enables consistent validation.

3. **Profile Immutability**: The `meta.profile` value MUST be set at extraction time and MUST NOT be modified thereafter. An artifact's profile is fixed for its lifetime.

4. **Upward Compatibility**: A Core Profile artifact may be re-extracted as Extended or Full. A Full Profile artifact may not be downgraded. Profile changes require re-extraction from source content.

5. **Governance Independence**: Profile selection does not affect governance treatment. A Core Profile artifact is subject to the same governance rules as a Full Profile artifact. Governance is determined by the Governance domain fields, not by profile.

## 3.7.7 Profile Selection Guidance

| Use Case | Recommended Profile | Rationale |
|----------|---------------------|-----------|
| Memory platform | Core | Minimal footprint, session coherence |
| Agent framework | Core | Lightweight emotional grounding |
| Journaling app | Extended | Narrative depth without clinical overhead |
| Companion AI | Extended | Longitudinal context with emotional topology |
| Workplace wellness | Extended | Coaching context with relational dynamics |
| Therapy platform | Full | Regulatory compliance, clinical completeness |
| Clinical tool | Full | Full manifold required |
| VitaPass binding | Any (Sealed) | Binding requires Sealed conformance, not a specific profile |
