# releases/

Versioned whitepaper documents, archived in-repo alongside the Zenodo deposits.

## Convention

Each released specification version gets a directory `releases/vX.Y.Z/`
containing the canonical whitepaper as published:

- `EDM_vX_Y_Z_Whitepaper_Harvey_YYYY.docx` — the authored document (the file
  deposited on Zenodo)
- `EDM_vX_Y_Z_Whitepaper_Harvey_YYYY.pdf` — PDF export of the same document

The Zenodo version DOI for each release is recorded in `CHANGELOG.md` and
`docs/RELEASE-NOTES.md`. The repository copy and the Zenodo deposit MUST be
byte-identical for the .docx; if they differ, the Zenodo deposit is canonical.

## Notes

- `releases/v0.8.0/` — the .docx matches the Zenodo deposit
  (10.5281/zenodo.19555166, 467,967 bytes). Zenodo hosts no PDF for v0.8.0;
  the PDF here (if present) is a repo-generated export for convenience and is
  not a published artifact.
- Versions prior to v0.8.0 were not archived in-repo at release time. Known
  local copies of historical whitepapers exist outside this repository; they
  can be backfilled into `releases/` if desired (see Zenodo for the published
  artifacts of record).
