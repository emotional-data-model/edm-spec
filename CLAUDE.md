# deepadata-edm-spec

The schema that defines significance artifacts.

## What This Repo Is

The canonical specification for EDM (Emotional Data Model) —
the structured artifact format that encodes what mattered at
capture time. This is the open standard. Everything else in
the DeepaData ecosystem implements or consumes this spec.

- **Current version:** v0.8.0
- **License:** MIT (open standard)
- **Zenodo DOI:** 10.5281/zenodo.19555166
- **Remote:** github.com/emotional-data-model/edm-spec

## Role in the DeepaData System

```
→ edm-spec (schema definition) ← YOU ARE HERE
       ↓ consumed by
   edm-sdk (extraction engine)
       ↓ consumed by
   deepadata-com (platform, sealing, registry)
       ↓ referenced by
   emotionaldatamodel.org (public standards site)
```

This repo defines the artifact format. It does not extract,
seal, or verify — those happen downstream.

## What This Repo Contains

- `schema/edm.v0.8.essential.schema.json` — Essential profile (5 domains, 24 fields)
- `schema/edm.v0.8.extended.schema.json` — Extended profile (8 domains, 50 fields)
- `schema/edm.v0.8.full.schema.json` — Full profile (10 domains, 96 fields)
- `schema/fragments/*.json` — Shared domain schemas
- `docs/` — Normative documentation
- `examples/*.ddna.json` — Validated example artifacts

## Hard Constraints

| Constraint | Reason |
|---|---|
| Do not modify schema without versioning policy | Breaking changes require migration path |
| Interpretation only, never inference | EU AI Act — fields contain explicit content only |
| Tooling is non-normative | SDK/CLI are reference implementations |

**Schema Freeze:** Do not modify field semantics without reading
`VERSIONING_POLICY.md` in deepadata-com. The spec is the contract.

## Domain Structure

```
Representational: CORE, CONSTELLATION, MILKY_WAY, GRAVITY, IMPULSE
Infrastructure:   META, GOVERNANCE, TELEMETRY, SYSTEM, CROSSWALKS, EXTENSIONS
```

## Profiles

| Profile | Domains | Fields | Certification eligible |
|---|---|---|---|
| Essential | 5 | 24 | Compliant, Sealed |
| Extended | 8 | 50 | Compliant, Sealed, Certified |
| Full | 10 | 96 | Compliant, Sealed, Certified |

## Source of Truth

For full project context, cross-repo state, and architectural decisions:

→ **See `deepadata-com/planning/CLAUDE_PROJECT.md`**

The platform repo (deepadata-com) is the source of truth for
session state, version alignment, and task tracking.

## OSS Boundary

This repo is MIT licensed and lives in the `emotional-data-model`
GitHub org. It is the open standard. Commercial extraction prompts,
sealing keys, and registry logic live in `deepadata-com` (UNLICENSED).

Do not copy commercial IP into this repo.
