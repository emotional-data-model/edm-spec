# Draft GitHub release — EDM v0.8.1

**Tag:** `v0.8.1` · **Target:** `main` · **Title:** `EDM v0.8.1 — references & errata patch`

Attach: `releases/v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.docx`,
`releases/v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.pdf`

---

## EDM v0.8.1

Patch release. **References and errata only — zero semantic change per §11.**
No schema files, field definitions, enumerations, or crosswalks are modified.
v0.8.0 artifacts are v0.8.1 artifacts; no migration required.

### Added

- **§14.6 reference** — Sofroniew, N., Kauvar, I., Saunders, W., Chen, R.,
  et al. (2026). *Emotion Concepts and their Function in a Large Language
  Model.* Anthropic, Transformer Circuits. arXiv:2604.07729. Mechanistic
  interpretability evidence that affective context causally influences model
  behaviour while remaining invisible in outputs.
- **§2.2** — one closing sentence recording this as direct mechanistic
  evidence for EDM's position: model-internal emotion representations are
  real, causally influence behaviour, and leave no trace in output text —
  affective context cannot be governed at the output layer.
- **`releases/`** — versioned whitepaper documents now archived in-repo
  (v0.8.0 docx is byte-identical to the Zenodo deposit; v0.8.1 ships docx + PDF).

### Errata

- Recorded the **reference-schema nullable-enum correction**: 24 nullable
  enumerated fields (constellation, gravity, impulse, milky_way) corrected in
  reference schemas to accept explicit `null` per §5.2 (*No Omission*).
  Implementation conformance fix — specification text unchanged.

### Changed

- Repository metadata refreshed to v0.8.1 (README was still citing v0.7.0 and
  its DOI throughout; CITATION.cff; package.json; docs/RELEASE-NOTES.md).
- CHANGELOG backfilled with a reconstructed v0.4.1 (2026-01-17) entry.

**Whitepaper DOI:** <!-- TODO(release): v0.8.1 Zenodo DOI -->
**Full changelog:** https://github.com/emotional-data-model/edm-spec/compare/v0.8.0...v0.8.1
