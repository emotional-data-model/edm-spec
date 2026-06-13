# Zenodo deposit description for EDM v0.8.1

Use as the record description (Zenodo accepts HTML; paste as rich text).
Title: `Emotional Data Model (EDM) v0.8.1` · Version: `v0.8.1` ·
Add related identifier: `isNewVersionOf` → `10.5281/zenodo.19555166`.

---

The Emotional Data Model (EDM) defines a governed, schema-bound
representational architecture for encoding affective context as a stable,
machine-interpretable data object, encapsulated in the .ddna envelope for
persistence, integrity, and sovereignty.

**v0.8.1 is a patch release: references and errata only, with zero semantic
change.** No schema structures, field semantics, or enumeration values are
added, modified, or removed; v0.8.0 artifacts are v0.8.1 artifacts.

Changes in this version:

- §14.6 adds Sofroniew, N., Kauvar, I., Saunders, W., Chen, R., et al.
  (2026), *Emotion Concepts and their Function in a Large Language Model*
  (Anthropic, Transformer Circuits; arXiv:2604.07729) — mechanistic
  interpretability evidence that model-internal emotion representations
  causally influence model behaviour while remaining invisible in output
  text.
- §2.2 records this evidence: affective context cannot be governed at the
  output layer, supporting EDM's explicit-representation position.
- An errata note records the reference-schema nullable-enum correction
  (24 fields accept explicit null per §5.2, *No Omission*); specification
  text unchanged.

This deposit includes the whitepaper in DOCX and PDF.

Version lineage: v0.4.0 through v0.7.0 are archived under concept DOI
10.5281/zenodo.17808652. v0.8.0 onward continues at concept DOI
10.5281/zenodo.19555165 (this record's lineage); the chains are cross-linked
via related identifiers.

Specification repository: https://github.com/emotional-data-model/edm-spec ·
Reference tooling: https://github.com/emotional-data-model/ddna-tools ,
https://github.com/emotional-data-model/ddna-reader ·
Site: https://www.emotionaldatamodel.org
