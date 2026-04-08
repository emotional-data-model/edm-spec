# EDM Significance Wiki Format

**Version:** 1.0
**Last Updated:** April 2026
**Status:** Informative guidance for EDM v0.7.0+

---

## Purpose

The EDM Significance Wiki Format defines a two-file pattern for rendering EDM artifacts as navigable markdown files weighted by significance. It enables agents and individuals to build personal knowledge bases where emotional history is structured, queryable, and governed.

This format is open. Anyone may implement a wiki generator that produces conforming output. The DeepaData reference implementation is available via the `deepadata-edm-mcp-server` package.

---

## The Two-File Pattern

Each source document (session, journal entry, conversation transcript) produces two files in a dated directory:

```
{output_dir}/
  {YYYY-MM-DD}-{source-name}/
    wiki_article.md
    significance_article.md
```

### wiki_article.md

Factual: what happened. LLM-compiled from source text. Contains:
- What happened (events, topics, participants)
- Who was involved (names, relationships)
- When and where (date, temporal context, location)
- Context links to related wiki articles

The wiki article is navigable context for human browsing and agent graph traversal.

### significance_article.md

Structured: why it mattered. EDM-derived from artifact fields. Contains significance fields from portable domains only:

**Portable domains (include):**
Core, Constellation, Gravity, Impulse, Milky_Way

**Non-portable domains (exclude):**
System, Extensions, Meta, Governance, Telemetry

---

## significance_article.md Schema

```markdown
---
arc_type: {string}
emotional_weight: {float 0.0-1.0}
identity_thread: {string}
recurrence_pattern: {acute|cyclical|chronic}
tether_type: {person|place|ritual|object}
artifact_id: {string}
captured_at: {ISO 8601 date}
---

# Significance — {source name} — {date}

## Arc Classification
- **arc_type:** {value}
- **triple_pattern:** {value if present}

## Emotional Weight
- **emotional_weight:** {value}
- **valence:** {positive|negative|mixed|neutral}
- **recurrence_pattern:** {value}

## Core Significance
- **anchor:** {value}
- **wound:** {value if present}
- **spark:** {value if present}
- **echo:** {value if present}

## Identity
- **identity_thread:** {value}
- **tether_type:** {value}
- **tether_target:** {value if present}

## Recall
- **recall_triggers:** {list if present}
- **somatic_signature:** {value if present}

## Narrative
{artifact.core.narrative — 3-5 sentences}

## Source Artifact
- **artifact_id:** {value}
- **captured_at:** {value}
- **profile:** {extended|full}
```

Omit any section where all fields are null or empty.

---

## YAML Frontmatter

The significance_article.md MUST include YAML frontmatter with at minimum:
- arc_type
- emotional_weight
- artifact_id
- captured_at

This enables agent grep and structured queries without reading the full file body.

---

## Index File

Implementations SHOULD maintain an index.md at the wiki root:

```markdown
# Significance Wiki Index

Generated: {timestamp}
Total articles: {count}

## By Arc Type
| Arc Type | Count | Avg Weight |
|----------|-------|------------|
| grief | 12 | 0.87 |
...

## Recent Articles
| Date | Source | Arc Type | Weight |
|------|--------|----------|--------|
...
```

---

## Agent Query Examples

An agent with access to the wiki directory can navigate it using standard file operations:

```bash
# Find all high-weight grief articles
grep -r "arc_type: grief" ./wiki/*/significance_article.md

# Find recurring identity threads
grep -r "identity_thread:" ./wiki/*/significance_article.md | sort

# Find chronic patterns
grep -r "recurrence_pattern: chronic" ./wiki/

# Find the highest emotional weight articles
grep -r "emotional_weight:" ./wiki/ | sort -t: -k2 -rn | head -10
```

---

## Conformance

A conforming significance_article.md:
- MUST include YAML frontmatter
- MUST include arc_type (if extractable)
- MUST include emotional_weight
- MUST include the Narrative section
- MUST NOT include System or Extensions fields
- MUST NOT include raw source text

A conforming wiki_article.md:
- MUST cover what happened, who, when/where
- SHOULD include context links to related articles
- MUST NOT reproduce the significance structure (separation is the design)

---

## Related Documents

- [PROFILES.md](PROFILES.md) — field selection by profile
- [SCOPE_AND_NONGOALS.md](SCOPE_AND_NONGOALS.md) — what EDM is and is not
- [OVERVIEW.md](OVERVIEW.md) — full field reference

---

**Status:** Informative (not normative)
**Contact:** jason@emotionaldatamodel.org
**Repository:** https://github.com/emotional-data-model/edm-spec
