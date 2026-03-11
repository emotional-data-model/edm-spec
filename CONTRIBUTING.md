# Contributing to the Emotional Data Model

Thank you for your interest in contributing to the EDM
open standard. This document covers how to contribute
to the repos in the `emotional-data-model` GitHub
organisation.

---

## What This Organisation Is

The `emotional-data-model` org maintains the open
standard for emotional data governance in AI systems.
Everything here is MIT licensed and vendor-neutral.

**Repos in scope for this guide:**
- `edm-spec` — the canonical JSON Schema and specification
- `ddna-tools` — open CLI/library for sealing, verifying,
  and inspecting `.ddna` artifacts
- `ddna-reader` — read-only CLI for inspection and
  structural validation
- `emotional_data_model_org` — the standards portal at
  emotionaldatamodel.org

**Out of scope:** Commercial platform repos live in the
`deepadata` org and are not open to external contribution.

---

## What We Welcome

- Bug reports and schema clarification issues
- Typo and documentation fixes
- Test case additions for the schema validation suite
- Crosswalk corrections for version migration files
- Tooling improvements to ddna-tools and ddna-reader
  (bug fixes, performance, compatibility)
- Translations of documentation
- Implementations in languages other than TypeScript

## What We Do Not Accept

- Changes to the extraction prompt or extraction logic
  (these are not part of the open standard)
- New fields or domains proposed without a companion
  spec discussion issue
- Breaking changes to existing schema without a formal
  deprecation process (see VERSIONING_POLICY.md)
- Dependencies from OSS repos on commercial
  (`deepadata` org) repos — see the boundary rules below

---

## Before You Start

**For bug fixes and small improvements:** Open an issue
first if the change is non-trivial. This prevents
duplicate work and ensures the fix aligns with the
project direction.

**For schema changes:** Open a spec discussion issue
before writing any code. Schema changes have downstream
consequences across multiple repos and require founder
review. New fields, domains, and profiles are MINOR
version changes — they follow the process in
VERSIONING_POLICY.md.

**For breaking schema changes:** These require explicit
founder sign-off. Open an issue with the label
`breaking-change` and wait for a response before
proceeding.

---

## Development Setup

### edm-spec

No build step — the spec is JSON Schema files and
documentation.

```bash
git clone https://github.com/emotional-data-model/edm-spec
cd edm-spec
```

To validate schema files:
```bash
npm install
npm test
```

### ddna-tools

```bash
git clone https://github.com/emotional-data-model/ddna-tools
cd ddna-tools
npm install
npm run build
npm test
```

### ddna-reader

```bash
git clone https://github.com/emotional-data-model/ddna-reader
cd ddna-reader
npm install
npm run build
npm test
```

---

## Schema Change Process

All schema changes must follow this process:

1. **Open a spec discussion issue** describing the
   proposed change and the use case it addresses

2. **Wait for discussion** — the maintainer reviews
   whether the change fits the standard's scope

3. **Classify the change** using VERSIONING_POLICY.md:
   - Breaking → MAJOR bump required
   - Additive → MINOR bump required
   - Clarification → PATCH

4. **Write the change** in a branch:
   - Update the relevant schema file(s)
   - Add or update crosswalk file if MINOR or MAJOR
   - Update CHANGELOG.md
   - Update documentation

5. **Open a pull request** — link to the spec discussion
   issue in the PR description

6. **Founder review** — all MINOR and MAJOR schema
   changes require explicit maintainer sign-off

---

## Pull Request Guidelines

- **One concern per PR** — do not bundle unrelated changes
- **Reference issues** — link to the issue your PR
  addresses
- **Test coverage** — new schema validation rules must
  include test cases
- **No commercial IP** — PRs must not contain content
  from the commercial `deepadata` platform, including
  extraction prompts, prompt fragments, or API logic
- **Crosswalk required** — MINOR and MAJOR schema changes
  must include a crosswalk file committed in the same PR

### Commit Message Format

```
type: short description

Longer explanation if needed.

Refs: #issue-number
```

Types: `fix`, `feat`, `docs`, `test`, `chore`, `schema`

---

## The OSS / Commercial Boundary

The `emotional-data-model` org is vendor-neutral. This
means:

**OSS repos must not:**
- Depend on any `deepadata` org repo at runtime
- Reference commercial API endpoints
- Bundle or document the extraction prompt
- Require a DeepaData API key for core functionality

**The sealing boundary (ddna-tools):**
`ddna-tools seal()` must execute locally using the
caller's own Ed25519 keys. No API call to DeepaData
is required or permitted for basic sealing. If you
see a DeepaData API call in the sealing path, that
is a bug — please report it.

---

## Normative Reference

The normative academic record for EDM is the published
whitepaper at Zenodo. When proposing changes to the
spec, contributors should frame their proposals in
relation to the published standard.

**Current version:** EDM v0.6.0
**DOI:** 10.5281/zenodo.18951891
**Previous version DOI:** 10.5281/zenodo.18883392

---

## Code of Conduct

This project follows standard open source conduct norms.
Be constructive, be precise, and be patient. Schema
discussions can be technical and detailed — that is
appropriate to the domain.

---

## Questions

Open an issue in the relevant repo. For questions about
the standard itself, use `edm-spec`. For tooling
questions, use `ddna-tools` or `ddna-reader`.

Email: jason@emotionaldatamodel.org
