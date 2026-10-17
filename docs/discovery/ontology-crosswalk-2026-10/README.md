# Ontology crosswalk discovery — October 2026

Discovery only. No schema, example or normative doc was modified. Everything here is input to a future v0.9 decision, not a decision.

| File | What it is |
|---|---|
| `REPORT.md` | Findings: grounding percentages, what is uniquely EDM, proposed adds/cuts, one-page v0.9 field list, ranked candidates for the ontology experiment, unverified-claims register |
| `fields.json` | Machine-read inventory of the 57 fields in the five affective domains (type, vocabulary, canonical values, description, profile membership) |
| `frameworks.json` | 39 reference frameworks with citations, fetch status, confidence, and extracted constructs/value sets (167 constructs) |
| `crosswalk.csv` | Full matrix: 242 rows (57 fields + 185 canonical values) × 39 frameworks; cell = relation + target + verification flag |
| `crosswalk.md` | Same mappings as readable per-field tables, plus Gap list A (orphans) and Gap list B (framework constructs with no EDM home) |
| `crosswalk_stats.json` | Counts used in the report |
| `coding-proposal.md` | Recommended code systems per categorical field, code+system+version+text shape, finer/coarser flags, SNOMED code table |
| `theoretical-conflicts.md` | Where the frameworks disagree and how EDM stays neutral |
| `naming-proposal.md` | Domain and field renames, full 57-row old→new table, value renames |

| `mfoem_classes.json` | Full extraction of the MFOEM OWL (version 2025-07-31): every class with CURIE, English label, definition, parents, synonyms, and emotion/mood/affective flags |
| `scripts/` | Generators: `inventory.py` (schema → `fields.json`), `mfoem_extract.py` (OWL → `mfoem_classes.json`), `merge_frameworks.py` (research extractions + MFOEM + Anthropic list → `frameworks.json`), `crosswalk_data.py` + `decisions_data.py` (the authored mapping and decisions), `crosswalk_build.py` (→ `crosswalk.csv`, `crosswalk.md`, `crosswalk_stats.json`) |
| `sources/` | Raw research extractions per framework group (`group_a_emotion.json` … `group_d_machine.json`) and the Anthropic 171-word list as extracted |

Reproduction:

```
python -I scripts/inventory.py <repo-root> fields.json
python -I scripts/mfoem_extract.py <MFOEM.owl> mfoem_classes.json
python -I scripts/merge_frameworks.py sources mfoem_classes.json sources/anthropic_171.json frameworks.json
python -I scripts/crosswalk_build.py fields.json frameworks.json .
```

The MFOEM OWL itself (640 KB) is not committed; fetch it from `http://purl.obolibrary.org/obo/mfoem.owl`.
