# EDM v0.8.0 — Implementation Profiles

## 3.7.1 Overview

EDM defines three implementation profiles that specify the minimum required fields for a conforming artifact. Profiles enable graduated adoption: memory platforms and agent frameworks may implement the lightweight Essential Profile, while regulated therapeutic applications require the Full Profile.

**Profiles are orthogonal to conformance levels (Section 3.8).** A profile defines WHAT is extracted — the depth of emotional representation. A conformance level defines HOW an artifact is governed — the trust and verification posture. Any profile may achieve any conformance level for which it is eligible.

## 3.7.2 Profile Declarations

A conforming artifact MUST declare its profile in the `meta.profile` field. Valid values are:

| Value | Profile |
|-------|---------|
| `"essential"` | Essential Profile |
| `"extended"` | Extended Profile |
| `"full"` | Full Profile |

The `meta.profile` field MUST be present and MUST contain one of the above values. Omission of this field renders the artifact non-conforming to EDM v0.6.0 and later.

## 3.7.3 Essential Profile (24 fields)

The Essential Profile defines the minimum viable artifact for session coherence and real-time retrieval. It is designed for memory platforms, agent frameworks, and AI assistants that require affective context without therapeutic depth.

### Included Fields

**Core**
- `anchor` — central theme
- `spark` — what triggered the memory
- `wound` — vulnerability or loss
- `fuel` — what energized the experience
- `bridge` — connection between past and present
- `echo` — what still resonates
- `narrative` — 3–5 sentence summary

**Constellation**
- `emotion_primary` — primary emotional classification
- `emotion_subtone` — array of supporting tones (may be empty)
- `narrative_arc` — narrative structure

### Essential Profile Use Cases

- Stateful session alignment
- Memory platform integration (Mem0, Zep, LangChain)
- Agent framework emotional grounding
- Memory compression and summarisation

## 3.7.4 Extended Profile (50 fields)

The Extended Profile provides full narrative and emotional topology without the complete salience geometry of the Full Profile. It is designed for journaling applications, companion AI with longitudinal context, and workplace wellness platforms.

### Included Fields

All Essential Profile fields, plus:

**Constellation** — all 18 fields required

**Milky_Way**
- `event_type` — event classification
- `location_context` — spatial context
- `associated_people` — array of related persons (may be empty)
- `visibility_context` — sharing scope
- `tone_shift` — tonal transition

**Gravity**
- `emotional_weight` — salience score 0.0–1.0
- `valence` — affective polarity
- `tether_type` — attachment classification
- `recurrence_pattern` — temporal pattern
- `strength_score` — retrieval strength 0.0–1.0

### Extended Profile Use Cases

- Companion AI with longitudinal memory
- Journaling and reflective writing applications
- Workplace wellness and coaching platforms
- Relational and temporal depth contexts

## 3.7.5 Full Profile

The Full Profile (96 fields) provides the complete representational manifold across all ten domains. It is required for regulated contexts and enterprise compliance.

### Required Domains and Fields

All ten domains MUST be fully populated. No field may be null unless the source content genuinely provides no basis for extraction. The extraction system MUST attempt population of all fields.

### Full Profile Use Cases

- Regulated therapy platforms
- Clinical documentation
- EU AI Act Article 5(1)(f) compliance documentation
- Enterprise audit and compliance
- Longitudinal subject registry entry (Full + Certified, future capability)
- DeepaData Certified conformance (see Section 3.8)

Note: Cross-vendor subject binding — portability of sealed artifacts across system boundaries — is available at Sealed conformance for all profiles, not Full only. Full Profile is required only for the longitudinal registry layer.

## 3.7.6 Partner Profiles

A Partner Profile is a named, versioned schema declaration that enables vertical-specific field selection within the EDM profile system.

### Profile ID Format

Partner profile IDs use reverse-DNS notation:

```
com.example.profilename.v1
```

Examples:
- `com.deepadata.journaling.v1`
- `com.deepadata.therapy.v1`
- `com.deepadata.companion.v1`
- `com.deepadata.wiki.v1`

### Relationship to Canonical Profiles

A partner profile declares:
- A base canonical profile (essential | extended | full)
- A subset of included_fields from that base profile
- An optional extensions_schema with a partner namespace

Extraction always runs to the declared base canonical profile. Profile Completeness invariant applies at extraction time. The partner profile filters the API response, not the extraction. The full artifact is stored server-side.

### meta.profile Field

In v0.8.0, meta.profile accepts:
- Canonical values: `essential`, `extended`, `full`
- Partner profile IDs: any string not matching a canonical value triggers registry resolution

This follows the same two-tier pattern as arc_type: canonical enum values remain valid; non-canonical values are accepted as strings and resolved via registry.

### Certification Minimum Bar

Partner profile artifacts are certification eligible when they contain a minimum of 10 populated affective fields from the 57-field affective set.

The 57 affective fields are those within the Core, Constellation, Milky_Way, Gravity, and Impulse domains.

Meta, Governance, Telemetry, System, and Extensions fields do not count toward the certification minimum.

### Interoperability

Canonical fields in a partner profile artifact are fully interoperable. Any EDM v0.8.0+ conforming reader can interpret canonical fields without knowing the partner profile.

Extensions fields require bilateral agreement per Section 3.9. Readers without the partner extensions schema MUST ignore those fields gracefully.

VitaPass portability is unaffected. Portable domains (Core, Constellation, Gravity, Impulse, Milky_Way) remain portable regardless of partner profile.

### Registry Resolution

Conforming readers encountering an unknown meta.profile value MUST:
1. Query the partner profile registry
2. Resolve to base profile + included_fields manifest
3. Validate against resolved schema

Canonical profiles remain valid without registry lookup.

### Reference Profiles

The following reference partner profiles are maintained by DeepaData:

| Profile ID | Base | Fields | Use Case |
|---|---|---|---|
| `com.deepadata.journaling.v1` | extended | 16 | Journaling AI, identity continuity |
| `com.deepadata.therapy.v1` | full | 24 | Therapy AI, session continuity |
| `com.deepadata.companion.v1` | extended | 18 | Companion AI, relational depth |
| `com.deepadata.wiki.v1` | extended | 17 | Significance wiki generation |

---

## 3.7.7 Profile Invariants

The following invariants apply to all profiles:

1. **Profile Completeness**: An artifact MUST contain only the domains defined for its declared profile. Domains not defined for the declared profile MUST be omitted. Inclusion of undeclared domains renders the artifact non-conforming.

2. **Exact Field Set**: An artifact MUST contain only the fields defined for its declared profile. Fields not defined for the declared profile MUST be omitted. Omission of required fields is prohibited.

3. **Profile Immutability**: The `meta.profile` value MUST be set at extraction time and MUST NOT be modified thereafter. An artifact's profile is fixed for its lifetime.

4. **Upward Compatibility**: A Essential Profile artifact may be re-extracted as Extended or Full. A Full Profile artifact may not be downgraded. Profile changes require re-extraction from source content.

5. **Governance Independence**: Profile selection does not affect governance treatment. A Essential Profile artifact is subject to the same governance rules as a Full Profile artifact. Governance is determined by the Governance domain fields, not by profile.

## 3.7.8 Profile Selection Guidance

| Use Case | Recommended Profile | Rationale |
|----------|---------------------|-----------|
| Memory platform | Essential | Minimal footprint, session coherence |
| Agent framework | Essential | Lightweight emotional grounding |
| Journaling app | Extended | Narrative depth without clinical overhead |
| Companion AI | Extended | Longitudinal context with emotional topology |
| Workplace wellness | Extended | Coaching context with relational dynamics |
| Therapy platform | Full | Regulatory compliance, clinical completeness |
| Clinical tool | Full | Full manifold required |
| Cross-vendor subject binding | Any (Sealed) | Binding requires Sealed conformance, not a specific profile |
