# Migration Guide

This guide explains how to migrate EDM data and code between schema versions.

---

## v0.5.1 → v0.6.0

**Normative schema:** [`schema/edm.v0.6.schema.json`](../schema/edm.v0.6.schema.json)

### Breaking Changes

**New required field: `meta.profile`**

EDM v0.6.0 introduces Implementation Profiles. The `meta.profile` field is now required for conformance.

- **Field:** `meta.profile`
- **Type:** string (required)
- **Valid values:** `"essential"`, `"extended"`, `"full"`
- **Impact:** Artifacts without `meta.profile` are non-conforming to v0.6.0

### Migration Steps

1. **Add `meta.profile` to all artifacts**
   ```json
   {
     "meta": {
       "profile": "full",
       ...
     }
   }
   ```

2. **Choose the appropriate profile:**
   - `"essential"` — Minimal footprint (~20 fields). Memory platforms, agent frameworks.
   - `"extended"` — Narrative depth (~45 fields). Journaling, companion AI.
   - `"full"` — Complete manifold (96 fields). Regulated contexts, certification.

3. **Ensure profile completeness**
   Include only the domains defined for your declared profile. Domains outside the profile MUST be omitted.

4. **Exact field set**
   Include only the fields defined for your declared profile. Fields outside the profile MUST be omitted.

### Profile Selection Guide

| Use Case | Profile |
|----------|---------|
| Memory platform / Agent framework | `essential` |
| Journaling / Companion AI | `extended` |
| Therapy platform / Clinical / Compliance | `full` |

See [PROFILES.md](PROFILES.md) and [CONFORMANCE.md](CONFORMANCE.md) for full details.

---

## v0.3 → v0.4

**Canonical crosswalk:** [`schema/crosswalks/v0.3_to_v0.4.json`](../schema/crosswalks/v0.3_to_v0.4.json)  
**Normative schema:** [`schema/edm.v0.5.schema.json`](../schema/edm.v0.5.schema.json)

### Summary of Changes

**6 fields deleted:**
- `meta.session_id` - Redundant with created_at + parent_id
- `constellation.affective_clarity` - Unclear definition
- `constellation.active_motivational_state` - Redundant with IMPULSE domain
- `milky_way.media_context` - Overlaps with media_format
- `milky_way.memory_layers` - Unclear origin
- `gravity.tether_target` - Redundant with core.anchor

**New domain:**
- `governance` - Now a required top-level domain (split from META)

**6 fields moved from META to GOVERNANCE:**
- `jurisdiction`
- `retention_policy`
- `exportability`
- `subject_rights`
- `masking_rules`
- `policy_labels`

**New in GOVERNANCE:**
- `k_anonymity` - K-anonymity tracking

### Migration Steps

See the detailed migration guide: [`docs/V04_MIGRATION_GUIDE.md`](V04_MIGRATION_GUIDE.md)

---

## v0.2 → v0.3

**Canonical crosswalk:** [`schema/crosswalks/v0.2_to_v0.3.json`](../schema/crosswalks/v0.2_to_v0.3.json)  
**Normative schema:** [`schema/edm.v0.3.schema.json`](../schema/edm.v0.3.schema.json)

### What stayed the same (selected)
- `core`: `anchor`, `spark`, `wound`, `fuel`, `bridge`, `echo`, `narrative`
- `constellation`: `emotion_primary`, `emotion_subtone`, `identity_thread`, `meaning_inference`, `relational_perspective`, `symbolic_anchor`, `temporal_rhythm`, `transcendent_moment`, `narrative_arc`, `temporal_context`, `relational_dynamics`, `memory_type`, `archetype_energy`
- `milky_way`: `visibility_context`, `tone_shift`, `associated_people`, `location_context`, `media_context`, `memory_layers`
- `gravity`: `emotional_weight`, `recall_triggers`, `legacy_embed`, `reentry_score`, `tether_type`, `tether_target`, `strength_score`, `emotional_density`, `valence`, `viscosity`, `gravity_type`, `temporal_decay`
- `meta`: `version`, `id`, `locale`, `created_at`, `updated_at`, `tags`
- `meta.source`: `channel`, `media_format`

### Renamed
- `impulse.visibility` → `impulse.social_visibility`
- `system.crosswalk_refs` → `system.crosswalks`

### Moved / Retyped
- `governance.compliance_mask` → `gravity.compliance_mask`
  - **transform:** string/flags → object `{ exportable:boolean, shareable:boolean, purpose_limited_to:string[] }`
- `crosswalks.*` → `system.crosswalks.*`
  - **transform:** flattened → structured keys (`plutchik_primary`, `geneva_emotion_wheel`, `DSM5_specifiers`, `HMD_v2_memory_type`, `ISO_27557_labels`)

### Introduced (new in v0.3)
- `constellation`: `higher_order_emotion`, `meta_emotional_state`, `interpersonal_affect`, `active_motivational_state`
- `milky_way`: `event_type`, `time_range.start`, `time_range.end`
- `gravity`: `entry_strength`, `resilience_markers[]`, `adaptation_trajectory`, `reinforcement_pulses[]`, `compliance_mask`
- `impulse`: `primary_energy`, `drive_state`, `motivational_orientation`, `moral_valence`, `temporal_focus`, `directionality`, `social_visibility`, `urgency`, `risk_posture`, `agency_level`, `regulation_state`, `attachment_style`, `coping_style`
- `governance`: `jurisdiction`, `retention_policy.{basis,ttl_days,on_expiry}`, `subject_rights.{portable,erasable,explainable}`, `k_anonymity.{k,groups[]}`
- `telemetry`: `entry_confidence`, `extraction_model`, `extraction_notes`, `retrieval_stats.{last_accessed_at,times_accessed,last_rank,avg_rank}`, `feedback[]`
- `system`: `embeddings[]`, `indices.waypoint_ids[]`, `indices.sector_weights.{emotional,episodic,semantic,procedural,reflective}`, `crosswalks.{plutchik_primary,geneva_emotion_wheel,DSM5_specifiers,HMD_v2_memory_type,ISO_27557_labels}`

### Deprecated
- `system.embedding_id`
- `system.crosswalk_refs`

---

## Migration tips

1. **Validate first**  
   Use the canonical schema and the repo’s validation script/CI to see where objects fail before migrating.

2. **Apply the crosswalk**  
   - Copy unchanged fields as-is.  
   - Apply `renamed` and `moved` mappings.  
   - Initialize new fields to `null`, `[]`, or sensible defaults per schema when absent.

3. **Watch transforms**  
   Any lossy conversion (e.g., retyping `compliance_mask`) should emit warnings in your migration tooling and be captured in logs.

4. **Re-validate**
   Run validation again after migration. Include only the domains defined for your declared profile.

---

## v0.1 → v0.2

**Canonical crosswalk:** [`schema/crosswalks/v0.1_to_v0.2.json`](../schema/crosswalks/v0.1_to_v0.2.json)

Summary:
- Moved several affective fields from `core` into `constellation` (e.g., `emotion_primary`, `narrative_arc`, `temporal_context`, `relational_dynamics`, `memory_type`, `media_format`).
- Introduced/standardized gravity metrics (`emotional_weight`, `emotional_density`, `valence`, `viscosity`, `temporal_decay`, `reentry_score`, `strength_score`, `tether_type`, `tether_target`, `recall_triggers`), replacing earlier V1 “gravity” descriptors.
- See the crosswalk file for the exact field-by-field mapping.
