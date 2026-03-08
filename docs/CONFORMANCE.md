# EDM v0.6.0 — Conformance Levels

## 3.8.1 Overview

EDM defines three conformance levels that specify how an artifact is governed and verified. Conformance levels enable graduated trust: development environments may operate at Compliant level, production platforms may seal artifacts for tamper-evidence, and regulated contexts may require third-party certification.

**Conformance levels are orthogonal to implementation profiles (Section 3.7).** A conformance level defines HOW an artifact is governed — the trust and verification posture. A profile defines WHAT is extracted — the depth of emotional representation. The two dimensions compose independently.

## 3.8.2 Conformance Level Definitions

### Level 1 — Compliant

A Compliant artifact is a valid EDM JSON object that conforms to the declared profile schema. Governance metadata is self-declared by the producing system. No cryptographic signing is required.

**Requirements:**

1. The artifact MUST validate against the EDM schema for the declared profile
2. The `governance.consent_basis` field MUST contain a valid legal basis
3. The `governance.jurisdiction` field MUST declare the applicable legal regime
4. The `meta.profile` field MUST be present and valid
5. All profile-required fields MUST be populated per Section 3.7

**Eligible Profiles:** Core, Extended, Full

**Use Cases:**
- Development and testing environments
- Memory platforms in stateless mode
- Agent frameworks requiring emotional grounding
- Internal analytics without external audit requirements

**Notes:**
- Compliant artifacts carry no cryptographic proof of integrity
- Governance metadata may be modified after creation
- Suitable for ephemeral contexts where tamper-evidence is not required

### Level 2 — Sealed

A Sealed artifact is encapsulated in a `.ddna` envelope with a W3C Data Integrity Proof. The producing system self-signs the artifact, providing cryptographic tamper-evidence. Governance metadata travels immutably with the artifact.

**Requirements:**

1. All Level 1 (Compliant) requirements MUST be satisfied
2. The artifact MUST be encapsulated in a valid `.ddna` envelope
3. The envelope MUST contain a W3C Data Integrity Proof (eddsa-jcs-2022 or equivalent)
4. The `meta.owner_user_id` field MUST be populated with a valid subject identifier
5. The proof MUST be verifiable using the declared verification method

**Eligible Profiles:** Core, Extended, Full

**VitaPass Binding:**

Sealed artifacts at any profile are eligible for VitaPass binding. The `meta.owner_user_id` field carries the `vp_id` address, making the artifact discoverable and presentable across vendor boundaries via the VitaPass consent rail. Profile depth does not affect VitaPass eligibility — a Core Profile Sealed artifact is equally addressable as a Full Profile Sealed artifact.

**Use Cases:**
- Platforms storing emotional data beyond session boundaries
- Enterprise B2B data exchange
- Data portability across system boundaries
- Audit trail requirements without third-party attestation

**Stateless TTL Enforcement:**

Unsealed artifacts containing populated sensitive domains (Milky_Way and Gravity) MUST be either nulled or sealed within 24 hours of creation. This maximum retention period applies regardless of session state. Systems MAY enforce a shorter window. The 24-hour limit is a regulatory backstop aligned with data minimisation principles.

**Notes:**
- Self-signed proofs establish tamper-evidence, not third-party trust
- Sealed artifacts may be verified by any party with access to the verification method
- Modification of any artifact field after sealing invalidates the proof

### Level 3 — Certified

A Certified artifact is a Sealed artifact that has been countersigned by DeepaData as a trusted certification authority. The certification proof attests to schema conformance, governance completeness, consent basis validity, and jurisdiction-appropriate field handling.

**Requirements:**

1. All Level 2 (Sealed) requirements MUST be satisfied
2. The artifact MUST use the Full Profile (`meta.profile = "full"`)
3. The `.ddna` envelope MUST contain a DeepaData Certification Proof
4. The certification proof MUST be issued by a DeepaData certification endpoint
5. ESAA (Emotional Safety Attestation) MUST be included for Full Profile artifacts

**Eligible Profiles:** Full only

Core and Extended profiles are NOT eligible for Certified conformance. This restriction ensures that regulatory compliance claims are backed by complete representational depth.

**Use Cases:**
- EU AI Act Article 5(1)(f) compliance documentation
- Regulated therapy and clinical platforms
- Enterprise procurement requiring third-party audit trail
- Insurance and liability contexts
- VitaPass longitudinal registry entry (trajectory state layer — future capability)

**Notes:**
- Certification is a commercial service provided by DeepaData
- Certified artifacts carry third-party attestation of conformance
- The certification proof chain is independently verifiable
- VitaPass binding (cross-vendor portability) is available at Sealed level for all profiles. Certified conformance is required only for registry-level longitudinal trajectory — a planned future capability.

## 3.8.3 Profile × Conformance Matrix

The following matrix shows all valid combinations of profile and conformance level:

| Profile | Compliant | Sealed | Certified |
|---------|-----------|--------|-----------|
| Core | ✓ | ✓ | ✗ |
| Extended | ✓ | ✓ | ✗ |
| Full | ✓ | ✓ | ✓ |

**Key:**
- ✓ — Valid combination
- ✗ — Invalid combination (Core and Extended are ineligible for Certified)

## 3.8.4 Conformance Verification

### Compliant Verification

A Compliant artifact is verified by:
1. Parsing the JSON structure
2. Validating against the EDM schema for the declared profile
3. Confirming required governance fields are present and valid

No cryptographic operations are required.

### Sealed Verification

A Sealed artifact is verified by:
1. Parsing the `.ddna` envelope structure
2. Extracting the W3C Data Integrity Proof
3. Resolving the verification method from the proof
4. Verifying the cryptographic signature over the canonicalised artifact
5. Confirming the artifact payload validates as Compliant

Verification fails if any signature check fails or if the payload is non-conforming.

### Certified Verification

A Certified artifact is verified by:
1. Completing all Sealed verification steps
2. Extracting the DeepaData Certification Proof from the envelope
3. Verifying the certification signature against DeepaData's public key
4. Confirming the certification proof references the artifact's content hash
5. Optionally validating the certification timestamp and expiry

Verification fails if the certification proof is missing, invalid, expired, or does not match the artifact content.

## 3.8.5 Conformance Progression

Artifacts may progress through conformance levels but not regress:

| From | To | Permitted |
|------|-----|-----------|
| Compliant | Sealed | ✓ |
| Compliant | Certified | ✓ (Full Profile only) |
| Sealed | Certified | ✓ (Full Profile only) |
| Sealed | Compliant | ✗ |
| Certified | Sealed | ✗ |
| Certified | Compliant | ✗ |

An artifact sealed at one conformance level retains that level. Downgrade is not permitted because it would invalidate the existing proof chain.

## 3.8.6 Stateless Mode Interaction

Stateless mode (Section 3.6) interacts with conformance levels as follows:

- **Stateless + Compliant**: Valid. The default path for memory platforms. Sensitive domains must be nulled within 24 hours.
- **Stateless + Sealed**: Not meaningful. Sealing implies persistence intent; stateless implies ephemerality. Systems SHOULD seal before the 24-hour TTL if persistence is intended.
- **Stateless + Certified**: Not meaningful. Certification implies long-term governance commitment.

Stateless mode is a governance decision, not a conformance level. Any profile can operate in stateless mode at Compliant level.

## 3.8.7 Commercial Considerations

- **Compliant** and **Sealed** conformance may be achieved using open-source tooling (deepadata-ddna-tools) without DeepaData involvement
- **Sealed** artifacts may be created using self-managed keys or DeepaData-provisioned keys
- **Certified** conformance requires DeepaData certification API access, which is a commercial service
- Certification pricing is available at https://deepadata.com/pricing
