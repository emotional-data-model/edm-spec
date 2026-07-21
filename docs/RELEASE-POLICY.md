# Release Policy — the One-Story Release Gate

**Status:** Adopted with the v0.8.3 release (founder decision lineage:
deepadata-com `planning/EDM_SPEC_0.8.2_LINEAGE_FINDINGS.md` §5,
2026-07-07; adopted 2026-07-21).

**Why this exists.** edm-spec@0.8.2 shipped to npm with a complete machine
crosswalk but no human-facing document: CHANGELOG, RELEASE-NOTES, and
README stopped at 0.8.1, and the published v0.8.1 whitepaper described a
`narrative_archetype` vocabulary (14 values, "structural role") that the
0.8.2 machine rejected (12 identity archetypes). For a specification whose
commercial layer is certification, a version whose document and machine
disagree is a trust defect. The one-story lineage was broken at the
document layer; v0.8.3 repaired it and this policy prevents recurrence.

## The gate

1. **One document per release.** Every release folds its confirmed
   semantic changes into one document release: CHANGELOG entry,
   `docs/RELEASE-NOTES.md` entry, README refresh, machine crosswalk in
   `schema/crosswalks/`, and — for releases that change what the
   whitepaper describes — a regenerated whitepaper in `releases/v<x.y.z>/`.

2. **npm + Zenodo publish together.** A release is published to npm and
   deposited on Zenodo as one act, keeping the version lineage unified
   under the concept DOI (10.5281/zenodo.17808652). No npm-only releases.

3. **Machine MAY lead the document between releases** — that is the
   ADR-0030 spec-first direction and is safe. **But** every npm release
   MUST have its document candidate staged before publish, and **no
   certification claim may cite a version whose document is not
   published.** While a machine version is ahead of its published
   document, certification language cites the newest version whose
   document HAS shipped.

4. **Field counts are machine-derived.** Any field count quoted in a
   document (composite descriptions, README, whitepaper) is the counted
   number of top-level fields in the shipped schema, never hand
   arithmetic. If the count in a document differs from the machine count,
   the machine count wins and the document is in error.

## Applied to the current lineage

- v0.8.2: npm-only, no document — the defect this policy exists to
  prevent. Its changelog entry was backfilled at v0.8.3 from
  `schema/crosswalks/v0.8.1_to_v0.8.2.json`.
- v0.8.3: document staged in-repo (CHANGELOG, RELEASE-NOTES, README,
  crosswalk, regenerated whitepaper in `releases/v0.8.3/`). npm publish
  and the Zenodo deposit are founder actions and happen together.
- Until the v0.8.3 deposit is published, certification language cites
  v0.8.1 (the newest version with a published document).
