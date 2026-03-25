# EDM Compliance Guide for the EU AI Act

**Version:** 1.0
**Last Updated:** March 2026
**Applicable Regulation:** EU Artificial Intelligence Act (Regulation 2024/1689)
**Key Deadline:** August 2, 2026 (High-Risk AI provisions)

---

## Executive Summary

The EU AI Act introduces the world's first comprehensive legal framework for artificial intelligence, with specific prohibitions on emotional recognition in workplace and educational contexts. This guide demonstrates how the Emotional Data Model (EDM) v0.6.0 provides **compliance-by-design** for organizations processing emotional data in AI systems.

**Key takeaway:** EDM's architectural principles—non-inferential representation, explicit consent, and governance-first design—directly address the EU AI Act's requirements for emotional AI systems.

---

## Regulatory Timeline

| Date | Milestone | Relevance to EDM |
|------|-----------|------------------|
| **Feb 2, 2025** | Article 5 prohibitions in force | Emotional recognition bans now enforceable |
| **Aug 2, 2025** | GPAI model rules apply | Foundation model governance |
| **Aug 2, 2026** | High-Risk AI rules apply | Full compliance required |

**Penalty for non-compliance:** Up to EUR 35,000,000 or 7% of worldwide annual turnover (whichever is higher).

---

## Article 5: Prohibited Practices

### 5(1)(a): Manipulation and Subliminal Techniques

**Prohibition:** AI systems using "subliminal techniques beyond a person's consciousness or purposefully manipulative or deceptive techniques" to distort behavior and impair decision-making.

**How EDM Addresses This:**

| EDM Principle | Compliance Mechanism |
|---------------|---------------------|
| **Non-inferential representation** | EDM fields contain only explicit, declared content—never latent psychological reconstructions |
| **No behavioral prediction** | The schema explicitly prohibits fields for behavioral inference or prediction |
| **Transparency** | All emotional data is visible, auditable, and explainable |

**Relevant EDM Fields:**
- `telemetry.extraction_model` — Documents what system extracted the data
- `telemetry.extraction_notes` — Provides transparency on extraction context
- `governance.subject_rights.explainable` — Enforces explainability requirement

### 5(1)(b): Exploitation of Vulnerabilities

**Prohibition:** AI systems exploiting vulnerabilities based on "age, disability or a specific social or economic situation" to distort behavior.

**How EDM Addresses This:**

| EDM Field | Compliance Function |
|-----------|---------------------|
| `governance.policy_labels` | Tags: `sensitive`, `children`, `health` for heightened protection |
| `governance.k_anonymity` | Prevents identification of vulnerable individuals |
| `governance.masking_rules` | Redacts identifying information |
| `meta.pii_tier` | Classifies sensitivity level (none/low/moderate/high/extreme) |

### 5(1)(c): Social Scoring

**Prohibition:** Classifying persons based on "social behaviour or known, inferred or predicted personal or personality characteristics" leading to detrimental treatment.

**How EDM Addresses This:**

EDM is designed for **individual emotional context**, not population-level scoring or classification:

- No aggregation primitives for population scoring
- `governance.exportability` controls prevent mass data extraction
- `meta.visibility` restricts data sharing scope
- Schema prohibits "inferred or predicted" personality characteristics

### 5(1)(f): Emotional Recognition in Workplace/Education

**Prohibition:** AI systems that "infer emotions of a natural person in the areas of workplace and education institutions" (except for medical/safety purposes).

**Critical distinction:** This prohibition applies to systems that **infer** emotions from biometric data. EDM operates differently:

| Prohibited (Inference) | Permitted (EDM Approach) |
|------------------------|--------------------------|
| Analyzing facial expressions to detect emotions | User explicitly declares emotional state |
| Voice analysis to infer mood | Text-based emotional context (explicitly permitted) |
| Biometric emotion detection | Non-biometric, user-provided emotional data |

**How EDM Maintains Compliance:**

1. **Non-biometric source types**: EDM `meta.source_type` supports `text`, which the EU AI Act explicitly permits for emotion detection
2. **No inference**: EDM fields must contain only "extracted or declared content"—never inferred emotions
3. **Explicit consent**: `meta.consent_basis` requires documented consent
4. **Medical/safety exceptions**: `governance.jurisdiction` and `governance.policy_labels` can document permitted use cases

**Relevant EDM Fields:**
```json
{
  "meta": {
    "profile": "essential",           // Profile declaration
    "source_type": "text",            // Not biometric
    "consent_basis": "consent",       // Explicit consent
    "source_context": "user_provided" // User-declared, not inferred
  },
  "governance": {
    "jurisdiction": "GDPR",
    "policy_labels": ["health"]       // If medical exception applies
  }
}
```

---

## High-Risk AI Requirements (August 2026)

For AI systems classified as high-risk (e.g., employment, education, essential services), the EU AI Act requires:

### Data Governance (Article 10)

| Requirement | EDM Implementation |
|-------------|-------------------|
| Data quality measures | `telemetry.entry_confidence` (0.0-1.0) |
| Bias examination | `governance.k_anonymity` for fair aggregation |
| Data relevance | `gravity.emotional_weight` for significance filtering |

### Transparency (Article 13)

| Requirement | EDM Implementation |
|-------------|-------------------|
| Understandable information | `telemetry.extraction_notes` |
| Appropriate level of detail | 24–96 field structured schema (profile-dependent) |
| Intended purpose disclosure | `meta.source_context` |

### Human Oversight (Article 14)

| Requirement | EDM Implementation |
|-------------|-------------------|
| Ability to understand system | 10-domain structured representation |
| Ability to intervene | `governance.subject_rights.erasable = true` |
| Override capabilities | `governance.exportability` controls |

### Record Keeping (Article 12)

| Requirement | EDM Implementation |
|-------------|-------------------|
| Automatic logging | `meta.created_at`, `meta.updated_at` |
| Traceability | `meta.id` (UUID), `meta.parent_id` |
| Audit trail | `.ddna` envelope with `audit_chain` |

### Data Retention

| Requirement | EDM Implementation |
|-------------|-------------------|
| Defined retention periods | `governance.retention_policy.ttl_days` |
| Lawful basis for retention | `governance.retention_policy.basis` |
| Expiry actions | `governance.retention_policy.on_expiry` (soft_delete/hard_delete/anonymize) |

---

## EDM Compliance Checklist

Use this checklist to verify EU AI Act compliance for EDM implementations:

### Prohibited Practices (Article 5)

- [ ] System does NOT infer emotions from biometric data in workplace/education
- [ ] If biometric emotion detection is used, it is for medical/safety purposes only
- [ ] No subliminal or manipulative techniques are employed
- [ ] No exploitation of vulnerable groups
- [ ] No social scoring based on emotional data

### Data Governance

- [ ] `meta.consent_basis` is set to valid value (consent, contract, legitimate_interest)
- [ ] `governance.jurisdiction` reflects applicable law
- [ ] `governance.subject_rights` are correctly configured
- [ ] `governance.retention_policy` defines lawful retention period

### Transparency

- [ ] `telemetry.extraction_model` documents the extraction system
- [ ] `telemetry.extraction_notes` provides context where needed
- [ ] All emotional data is auditable and explainable

### Subject Rights

- [ ] `governance.subject_rights.portable = true` (for data portability)
- [ ] `governance.subject_rights.erasable = true` (for right to erasure)
- [ ] `governance.subject_rights.explainable` reflects explanation capability

### Special Categories

- [ ] `governance.policy_labels` includes relevant tags (health, children, biometrics)
- [ ] `governance.masking_rules` configured for sensitive data
- [ ] `governance.k_anonymity` set for any aggregation use cases

---

## Permitted Use Cases

The EU AI Act permits emotional AI in specific contexts. EDM supports compliant implementation for:

### 1. Medical/Healthcare Applications

Emotional recognition for patient care, mental health assessment, or therapeutic purposes.

```json
{
  "meta": {
    "profile": "full",
    "source_context": "therapy_session",
    "consent_basis": "consent"
  },
  "governance": {
    "jurisdiction": "HIPAA",
    "policy_labels": ["health", "sensitive"],
    "subject_rights": {
      "portable": true,
      "erasable": true,
      "explainable": true
    }
  }
}
```

### 2. Safety Applications

Fatigue detection for drivers, stress monitoring for safety-critical roles.

```json
{
  "meta": {
    "profile": "essential",
    "source_context": "safety_monitoring",
    "consent_basis": "legitimate_interest"
  },
  "governance": {
    "jurisdiction": "GDPR",
    "policy_labels": ["none"],
    "retention_policy": {
      "basis": "legal",
      "ttl_days": 30,
      "on_expiry": "hard_delete"
    }
  }
}
```

### 3. Consumer Applications (Non-Workplace/Education)

Personal journaling, companion chatbots, legacy/memoir applications.

```json
{
  "meta": {
    "profile": "essential",
    "source_type": "text",
    "source_context": "personal_journaling",
    "consent_basis": "consent"
  },
  "governance": {
    "jurisdiction": "GDPR",
    "exportability": "allowed",
    "subject_rights": {
      "portable": true,
      "erasable": true,
      "explainable": false
    }
  }
}
```

---

## Implementation Recommendations

### For Developers

1. **Validate jurisdiction**: Always set `governance.jurisdiction` to the applicable regulatory regime
2. **Enforce consent**: Require explicit `consent_basis` before creating EDM artifacts
3. **Document extraction**: Populate `telemetry` fields for audit trail
4. **Respect retention**: Implement `retention_policy.on_expiry` actions automatically

### For Compliance Officers

1. **Audit regularly**: Review EDM artifacts for prohibited use patterns
2. **Train teams**: Ensure understanding of Article 5 prohibitions
3. **Document exceptions**: If using medical/safety exceptions, document thoroughly
4. **Monitor updates**: EU AI Act guidance continues to evolve

### For Product Managers

1. **Design for consent**: Build consent collection into user flows
2. **Avoid inference**: Use declared/extracted emotional data, not inferred
3. **Enable portability**: Users should be able to export their emotional data
4. **Plan for erasure**: Implement right-to-deletion workflows

---

## Relationship to .ddna Envelopes

For long-term emotional memory storage (beyond EDM's 24-hour session window), the **.ddna envelope** provides additional compliance guarantees:

| .ddna Feature | Compliance Benefit |
|---------------|-------------------|
| Cryptographic signing | Tamper-evident audit trail |
| Byte-stable payload | Verifiable integrity over time |
| Governance inheritance | Retention and consent preserved |
| Audit chain | Complete provenance history |

---

## Further Resources

- [EU AI Act Full Text](https://artificialintelligenceact.eu/)
- [Article 5: Prohibited Practices](https://artificialintelligenceact.eu/article/5/)
- [European Commission Guidelines (Feb 2025)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [EDM v0.7.0 Whitepaper](https://zenodo.org/records/19211903)

---

## Disclaimer

This guide provides general information about EU AI Act compliance as it relates to the EDM specification. It does not constitute legal advice. Organizations should consult qualified legal counsel for specific compliance questions.

---

**Contact:** jason@emotionaldatamodel.org
**Repository:** https://github.com/emotional-data-model/edm-spec
