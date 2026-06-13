# EDM v0.8.1 Patch Release + Spec-Estate Consolidation — Handoff

**Date:** 2026-06-12
**Prepared by:** Claude (unattended session, founder = Jason Harvey)
**Status:** Amended per founder decisions (2026-06-12), publish-ready.
Committed on local branch `release/v0.8.1`. All publish actions are
founder steps listed in §6.

Per the spec's own §11 discipline, every change made in this session is
enumerated (§4), classified, and traceable. Items outside the approved v0.8.1
floor are staged as pending (§3) and NOT implemented.

---

## 1. Connections map (Phase 0)

### 1.1 The two spec repos

| | `edm-spec` (canonical) | `deepadata-edm-spec` (legacy folder) |
|---|---|---|
| Remote | `github.com/emotional-data-model/edm-spec` | **same remote** |
| State at audit | local main 24 commits **behind** origin (stopped at v0.7.0, 2026-03-24) | main == origin/main (b3cae0d, 2026-04-22) |
| Local-only commits | none | none |
| Action taken | fast-forwarded to origin/main (b3cae0d) | untouched |

**Finding:** these are two clones of the *same* GitHub repository. There is no
separate legacy remote; the "migration" happened on GitHub (org transfer at
v0.6.0) and only the local folder name differs. Nothing landed in "legacy"
post-migration that isn't on origin — all v0.8.0 work was done from the
`deepadata-edm-spec` working copy and pushed. Working trees are identical
modulo CRLF/LF line endings (verified file-by-file); the legacy folder
additionally holds untracked `node_modules/`, `.claude/`, and a Windows `nul`
phantom file.

### 1.2 Inbound references across the estate

Verified remotes: `deepadata-edm-sdk`, `deepadata-edm-mcp-server`,
`deepadata-adapters` genuinely live at `github.com/deepadata/*`;
`ddna-tools` and `ddna-reader` live at `github.com/emotional-data-model/*`.
So `github.com/deepadata/deepadata-edm-sdk` links are **correct**, not stale.

Stale/incorrect references (NOT fixed — proposed corrections for approval;
some are published npm metadata):

| Where | What | Proposed correction |
|---|---|---|
| `emotionaldatamodel-org-OLD` (13+ files: app/*.tsx, CLAUDE.md, public/llms.txt) | `github.com/deepadata/deepadata-edm-spec` (~30 refs) | None — repo is superseded by `emotional_data_model_org`. Recommend archiving the OLD repo instead of fixing. |
| `deepadata-com/tests/fixtures/vectors/REFRESH.md`, `tests/conformance.test.ts:4,14`, `tests/vectors/scripts/generate-vectors.mjs:157`, `supabase/migrations/20260424120000_*.sql:2` | local-path references to `deepadata-edm-spec/…` | Update path strings to `edm-spec/…` (or make path configurable). Comment/docs-only; low risk. |
| `deepadata-ddna-reader/tests/conformance.test.ts:4`, `test-fixtures/vectors/scripts/generate-vectors.mjs:157` | same local-path references | same correction |
| `deepadata-ddna-tools/README.md:~315 area` + `public/llm.txt` | Zenodo DOI 10.5281/zenodo.19211903 (v0.7.0) | Bump to current version DOI after v0.8.1 publishes (add to backfill list §6.3) |
| `deepadata-profile/README.md` | DOI 19211903 (v0.7.0) | same backfill |
| `deepadata-edm-mcp-server/README.md:191`, `public/llm.txt:35` | DOI 19211903 (v0.7.0) | same backfill — **published npm metadata; needs a republish to take effect** |
| `edm-spec/README.md` | was citing v0.7.0/19211903 throughout | **fixed in this session** (part of v0.8.1, see §4) |

### 1.3 Whitepaper locations

| Location | Version | Format |
|---|---|---|
| Zenodo 10.5281/zenodo.19555166 | v0.8.0 | DOCX only — **no PDF was ever deposited**, though the site labels the link "Download whitepaper (PDF)" |
| `emotional_data_model_org/design-handoff/emotional-data-mpdel-update/project/uploads/EDM_v0_8_0_Whitepaper_Harvey_2026.docx` | v0.8.0 | DOCX — byte size (467,967) matches the Zenodo deposit |
| same folder, `whitepaper.txt` | v0.8.0 | full text dump (167 KB) |
| `edm-spec/releases/v0.8.0/` | v0.8.0 | DOCX — **copied there this session** (md5 5519a295cbb17531954f596adf8a42b9, identical to design-handoff copy) |
| `edm-spec/releases/v0.8.1/` | v0.8.1 | DOCX + PDF — **built this session** |
| `planning/edm-v0.6.0/` (GitHub root) | v0.6.0, v0.5.1 | DOCX |
| `planning/archive/EDM_v0.4.1_Whitepaper_Harvey_2026.docx` | v0.4.1 | DOCX |
| `jason-harvey-os/raw/Claude - Folder/` | v0.4.0 | DOCX + PDF |
| `deepadata-com` worktrees `planning/archive/Emotional_Data_Model__EDM__v0_4_1.txt`, `whitepaper_extract.txt` | v0.4.1 | text extracts (stale) |

### 1.4 Zenodo lineage (authoritative, from the Zenodo API)

Concept DOI **10.5281/zenodo.17808652** contains:

| Version | DOI | Published |
|---|---|---|
| v0.4.0 | 10.5281/zenodo.17808653 | 2025-12-04 |
| v0.4.0 (duplicate deposit) | 10.5281/zenodo.17808878 | 2025-12-04 |
| v0.5.0 | 10.5281/zenodo.18541956 | 2026-02-09 |
| v0.5.1 | 10.5281/zenodo.18883392 | 2026-03-06 |
| v0.6.0 | 10.5281/zenodo.18951891 | 2026-03-11 |
| v0.7.0 | 10.5281/zenodo.19211903 | 2026-03-25 |

**⚠ Lineage fork:** v0.8.0 (10.5281/zenodo.19555166, 2026-04-13) was deposited
as a **new Zenodo concept** (concept DOI 10.5281/zenodo.19555165), cross-linked
manually via `isNewVersionOf`/`isPreviousVersionOf` related identifiers. So
the concept DOI 17808652 currently resolves to **v0.7.0**, not the latest.
Consequences and the publish decision this forces are in §6.3.

**⚠ Other Zenodo facts:** there are two v0.4.0 deposits (17808653, 17808878 —
same date; one is presumably a redundant upload); v0.4.1 (git tag 2026-01-17,
W3C Data Integrity Proofs) **never had its own deposit** — its tag message
cites the concept DOI.

### 1.5 Website repo (emotional_data_model_org)

- Vite + React, **deployed via Vercel** (per README; no vercel.json or GitHub
  Actions in repo — deploys are triggered by Vercel's Git integration, so a
  push to the production branch publishes).
- Version strings hardcoded in components (Navigation, MetaStrip, Hero,
  Versions, Downloads, Citation) — no central version file.
- **⚠ The live VersionsSection table contains fabricated DOIs and wrong
  dates/notes** for v0.7.0 and earlier: it lists 15243817 (v0.7.0), 14992765
  (v0.6.0), 14205103 (v0.5.0), 14002003 (v0.4.0) — none of these exist in the
  real lineage (§1.4) — and e.g. describes v0.6.0 as "Impulse domain added,
  envelope renamed .ddna" which doesn't match the actual v0.6.0 changes
  (Implementation Profiles). It also omits v0.5.1 and misdates v0.5.0 as
  "November 2025". **Proposed correction:** replace rows with §1.4 table
  (founder approval — live content). Not included in the staged commit, which
  touches only the v0.8.1/v0.8.0 rows.
- Site labels the Zenodo link "Download whitepaper (PDF, v0.8.0 · 96 pp)" but
  the v0.8.0 deposit is DOCX-only. The v0.8.1 deposit should include the PDF
  (prepared) which fixes this going forward; staged commit updates the label
  to "v0.8.1 · 91 pp".

---

## 2. Markdown spec (Phase 0.5a)

**No monolithic markdown version of the spec exists.** Searched all repos
(including worktrees) for spec-shaped markdown (domain names
core/constellation/gravity/impulse together; "precedes computation"; §-numbered
sections). What exists:

| Candidate | Version | Nature |
|---|---|---|
| `edm-spec/docs/*.md` (OVERVIEW, PROFILES, CONFORMANCE, etc.) | tracks repo version | modular implementation docs, not the whitepaper; no §-numbering, no §5.2/§14 text |
| `emotional_data_model_org/design-handoff/…/uploads/whitepaper.txt` | v0.8.0 | full text dump of the published docx (167 KB) |
| `deepadata-com` worktrees `planning/archive/Emotional_Data_Model__EDM__v0_4_1.txt` and `whitepaper_extract.txt` | v0.4.1 | stale text extracts (4 minor versions behind) |

Drift: the v0.4.1 extracts predate profiles, conformance levels, partner
profiles, arc_type, extensions. No winner picked per instructions; if a
canonical markdown spec is wanted, the v0.8.1 docx is the source to convert
from.

---

## 3. Candidate table (Phase 0.5b) — pending items, NOT implemented

| # | Item | Provenance | What it proposes | Class |
|---|---|---|---|---|
| 1 | **Nullable-enum conformance errata** (24 fields) | ddna-tools branch `fix/schema-nullable-enums` @ `db2c449` (2026-06-12); commit msg self-identifies as "v0.8.1 errata candidate"; extraction-hardening handoff lines 147–150; diff archived at `pending/ddna-tools-db2c449-nullable-enums.diff` | Reference schemas list enum values without explicit `null` although fields are `type:["string","null"]`; spec §5.2 (No Omission) requires explicit null. ddna-tools' vendored copies fixed (20 of 23 failed sample artifacts now validate). **edm-spec's own `schema/` files need the same 24-field fix** (constellation ×6, gravity ×5, impulse ×10, milky_way ×1, + 2 inlined in extended schema). | **(a) v0.8.1** — errata note shipped (see §4); the schema-file edit itself is held for approval per the "floor only" instruction. Apply by transposing the archived diff (paths: ddna-tools `schemas/` → edm-spec `schema/`). |
| 2 | **`constellation.experiential_stance` field** | `deepadata-com/.claude/worktrees/feat-extraction-hardening/planning/proposals/2026-06-12-experiential-stance-v0.9.md` (132 lines, complete proposal); session handoff same date lines 34–76 | New nullable enum: `lived \| witnessed \| quoted_third_party \| assistant_generated \| hypothetical \| null`, all profiles, plus a normative constraint that non-lived stances MUST NOT encode non-subject material in subject-significance fields (weights floored ≤0.2). Production finding: **pre-guard sealed corpora cannot be repaired post-hoc** (seal freezes the misattribution), so the guard must be at extraction time and the field must be in-schema. SDK 0.8.9 (unpublished branch) carries an interim telemetry-only implementation; 105 tests passing. | **(b) v0.9** — schema-touching |
| 3 | **`meta.parent_id` profile placement** | edm-spec `schema/edm.v0.8.{essential,extended,full}.schema.json:59` (all three define `parent_id`); SDK `deepadata-edm-sdk/src/assembler.ts:83,448–452` (treats it as FULL-profile-only and strips it from essential/extended); extraction-hardening handoff lines 106–108 | Spec and implementation disagree: reference schemas permit `parent_id` in every profile, but the SDK's profile invariants strip it from essential/extended, so chunk lineage is lost from those artifacts (it survives only in platform-side chunk metadata). Spec must either (i) promote `parent_id` to all profiles (and the SDK keeps it), or (ii) state normatively that sub-full chunk lineage is metadata-layer and remove `parent_id` from the essential/extended reference schemas. | **(b) v0.9** — either resolution touches schemas/normative text |
| 4 | **Certification eligibility reconciliation** | Pricing page `deepadata-com/app/pricing/page.tsx:291,318–319` ("Full Profile artifacts only" / "Full Profile only"); ADR-0004 (2026-03-11, Accepted) made **Extended + Full** eligible; CONFORMANCE.md updated 2026-03-12 (`cdb33e1`); ADR-0012 Decision 6 (2026-04-07, founder-approved 2026-04-08) set the certification minimum bar at **10+ populated affective fields**; spec v0.8.0 PROFILES.md §3.7.6 and whitepaper §11.1 state the 10-field bar; session handoff 2026-03-12 line 31: "Pricing page completely invalidated by ADR-0004" | **Verdict: pricing page needs correction.** The rule WAS formally decided (ADR-0004 + ADR-0012) and IS stated in spec docs. The founder-recalled **≥15-field** threshold appears nowhere in any ADR, spec, plan, or handoff — the decided number is **10**. If 15 is the intended new bar, that is a fresh v0.9 policy decision, not a recovery of an old one. | Pricing-page fix = site/platform task (not spec). Any threshold change = **(b) v0.9** |
| 5 | **Full-profile-as-governed-tier principle** | Derived from #3 + #4: pricing page treats certification as full-only; SDK treats `parent_id` as full-only | Candidate stated principle for v0.9: "the Full profile is the governed tier" — certain governance/lineage capabilities exist only at Full. **Caution:** the evidence runs the other way on certification (ADR-0004/0012 deliberately opened certification beyond Full); adopting this principle would require revisiting those ADRs. Presented as a candidate for discussion, not a recommendation. | **(b) v0.9** policy item |
| 6 | **Whitepaper internal errata found this session** | v0.8.0/v0.8.1 docx: §11.1 lineage paragraph says "v0.8.0 introduces Implementation Profiles…" where the v0.6.0 release did (and the narrative skips v0.5.1/v0.6.0 labels); Appendix A `meta.version` constraint still reads `MUST match "0.7.x"` | Two text corrections, zero semantic change | **✓ RESOLVED** — founder-approved 2026-06-12. Both errata applied to make_v081_docx.py (para 362: "v0.8.0 introduces" → "v0.6.0 introduces"; para 439: "0.7.x" → "0.8.x"), docx rebuilt, PDF re-exported, CHANGELOG/RELEASE-NOTES updated. |
| 7 | **A-MBER reference** | Wen, D., Sun, K., & Wang, Y. (2026). A-MBER: Affective Memory Benchmark for Emotion Recognition. arXiv:2604.07017. | Inserted into §14.6 in house style per founder direction (Option A — the benchmark). | **✓ RESOLVED** — founder chose A-MBER (the benchmark, arXiv:2604.07017) 2026-06-12. Inserted into docx via make_v081_docx.py, PDF re-exported. |
| 8 | **ADR-0021 version-routed validation** | `deepadata-com/planning/ADR/ADR-0021…md`; SDK `edm-schema.ts:17–22` TODO | SDK validates v0.7 artifacts against v0.8 rules, violating §11.4; deferred to v0.9/v1.0 | **(b) v0.9** architectural (SDK-side, spec may need §11.4 clarification) |
| 9 | Governance enum alignment (bfe6c0c, d8e6601, 2026-04-24) | ddna-tools merged commits | jurisdiction/exportability/retention enum fixes | **(c) stale/superseded** — already merged; worth a one-time three-way audit (spec ↔ ddna-tools ↔ SDK) during v0.9 |
| 10 | Partner-profile manifest update "v0.8.1" (e057bba, 2026-04-16) | `deepadata-com/planning/EXECUTION_CHECKLIST.md:372–376` | adaptation_trajectory added to companion/journaling manifests | **(c) stale/superseded** — completed; note the "v0.8.1" label there refers to partner-profile manifest versioning, not this spec release |

| 11 | **Misuse and Dual-Use Considerations section** | Founder direction, 2026-06-12 | Normative framing of `visibility`, `masking_rules`, `pii_tier`, and `consent` scope as anti-manipulation controls, motivated by the explicit-record-as-manipulation-map risk and the governed-explicit vs ungoverned-latent argument (Sofroniew et al. 2026 as evidence the latent lever already exists). | **(b) v0.9 candidate** — founder-directed |

Non-spec critical items surfaced by the sweep (for awareness, on
`feat/extraction-hardening`, blocking production): retired Kimi model pinned in
prod (all /v1/activate* calls failing), Vercel prod deploy in ERROR state since
2026-05-06, TurboPuffer `recurrence_pattern` attribute drift.

---

## 4. What changed in this session (every changed line/file)

### 4.1 `edm-spec` repo (working tree; commit before publishing — see §6.1)

- **Fast-forwarded** local main 3f4418a → b3cae0d (origin/main; no local commits lost — there were none).
- **CHANGELOG.md**: added `[0.8.1] - 2026-06-12` entry (added/errata/changed/migration); added reconstructed `[0.4.1] - 2026-01-17` entry (marked as reconstructed); added 0.8.1 and 0.4.1 compare links.
- **README.md**: v0.7.0→v0.8.1 version strings; stale heading "DeepaData — EDM v0.6 (Specification)" → "Emotional Data Model — EDM (Specification)"; DOIs 19211903 → 19555166 with `TODO(release)` markers for the v0.8.1 DOI; schema filename refs v0.7→v0.8; clone path `cd deepadata-edm-spec` → `cd edm-spec`; canonical schema URLs v0.7.0→v0.8.0; emotion_primary enum list completed (+disappointment, relief, frustration — per schema fragment); arc_type list added; repo-structure block corrected to actual contents (+test-vectors/, releases/, CHANGELOG.md, real example filenames); migration entries added for 0.8.0→0.8.1 and 0.7.0→0.8.0; v0.6.0→v0.7.0 date fixed (April→March 2026); bibtex/citation → v0.8.1; both concept DOIs listed; footer version/date.
- **CITATION.cff**: title/version → 0.8.1, date-released 2026-06-12, DOI left at 19555166 with TODO(release) comments (×2).
- **package.json**: version 0.8.0 → 0.8.1.
- **docs/RELEASE-NOTES.md**: v0.8.1 section added (Current); v0.8.0 marked published with DOI; v0.7.0 demoted from "Current"; lineage table corrected with authoritative DOIs incl. v0.4.1 row and concept-DOI note.
- **releases/** (new): `README.md` (convention); `v0.8.0/EDM_v0_8_0_Whitepaper_Harvey_2026.docx` (byte-identical to Zenodo deposit); `v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.docx` + `.pdf` (91 pp) + `make_v081_docx.py` (the reproducible build script).
- **planning/2026-06-12-v0.8.1-consolidation/** (new): this handoff + `pending/ddna-tools-db2c449-nullable-enums.diff`.

### 4.2 v0.8.1 whitepaper docx — exact paragraph-level diff vs v0.8.0

Verified by independent re-extraction and full-document diff: **exactly 20
changed blocks, 1557 → 1560 paragraphs**; everything else byte-identical.
Page header: "EDM v0.8.0" → "EDM v0.8.1".

| ¶ | Change |
|---|---|
| 0, 2 | title / "Version:" → v0.8.1 |
| 3 | Date: March 2026 → June 2026 |
| 6 | DOI line → "pending — assigned on Zenodo publication (v0.8.0: 10.5281/zenodo.19555166)" |
| 19, 25, 34, 37, 50, 128, 132, 196, 197, 226, 327, 355, 381 | prose "EDM v0.8.0" → "EDM v0.8.1" (current-spec references only) |
| 46 (§2.2) | appended: "Recent interpretability work (Sofroniew et al., 2026) provides direct mechanistic evidence for this position: model-internal emotion representations are real, causally influence behaviour, and leave no trace in output text — confirming that affective context cannot be governed at the output layer." |
| 361 (§11.1 heading) | lineage chain extended "… → v0.8.0 → v0.8.1)" |
| 362 (§11.1) | **ERRATA**: "v0.8.0 introduces Implementation Profiles" → "v0.6.0 introduces Implementation Profiles" |
| after 364 (§11.1) | new lineage paragraph for v0.8.1 (patch; references+errata; zero semantic change; enumerates content items) |
| after 428 (§14.6) | new reference: Sofroniew, N., Kauvar, I., Saunders, W., Chen, R., et al. (2026). *Emotion Concepts and their Function in a Large Language Model.* arXiv:2604.07729. |
| after 428 (§14.6) | new reference: Wen, D., Sun, K., & Wang, Y. (2026). *A-MBER: Affective Memory Benchmark for Emotion Recognition.* arXiv:2604.07017. |
| 439 (Appendix A) | **ERRATA**: `MUST match "0.7.x"` → `MUST match "0.8.x"` |

Deliberately **unchanged**: historical lineage text (§11.1 ¶363–364), §11.5
deprecation entries, Appendix B (example artifacts remain v0.8.0 — no schema
change in this patch), `.ddna` payload_type examples, glossary schema
references.

### 4.3 `emotional_data_model_org` repo

Unpushed commit **9d33828** on branch **`release/v0.8.1`** (main untouched;
working tree returned to main). 7 files: Navigation, MetaStrip (DOI →
placeholder, date → June 2026), HeroSection ×2, DownloadsSection (label
v0.8.1 · 91 pp), VersionsSection (v0.8.1 row added with DOI placeholder;
v0.8.0 → archived), CitationSection (v0.8.1 + DOI placeholder), llms.txt
version line. `npm run build` passes. **DO NOT push until DOI backfill** —
the deploy mechanism is Vercel Git integration, so pushing the production
branch publishes.

---

## 5. Citation verification notes

### 5.1 Sofroniew et al. (2026) — VERIFIED, with one correction

- Title/venue confirmed: *Emotion Concepts and their Function in a Large
  Language Model*, Anthropic, Transformer Circuits (transformer-circuits.pub,
  published 2026-04-02). **arXiv ID exists: 2604.07729** (v1 2026-04-09) — added.
- Full author order (arXiv): Sofroniew, Kauvar, Saunders, Chen, Henighan,
  Hydrie, Citro, Pearce, Tarng, Gurnee, Batson, Zimmerman, Rivoire, Fish,
  Olah, **Lindsey (last)**. The drafted citation placed "Lindsey, J." fifth;
  that's not the paper's order, so the inserted reference uses
  "Sofroniew, N., Kauvar, I., Saunders, W., Chen, R., et al." If you want
  Lindsey named (e.g., as senior author), house style would be
  "…Chen, R., … Lindsey, J. (2026)" — easy to amend in the build script.

### 5.2 A-MBER — RESOLVED (founder chose Option A, 2026-06-12)

Same author trio (Deliang Wen, Ke Sun, Yu Wang):

- **Option A (the benchmark) — SELECTED:** Wen, D., Sun, K., & Wang, Y.
  (2026). A-MBER: Affective Memory Benchmark for Emotion Recognition.
  arXiv:2604.07017.
- **Option B (the system):** Wen, D., Sun, K., & Wang, Y. (2026). Memory Bear
  AI Memory Science Engine for Multimodal Affective Intelligence: A Technical
  Report. arXiv:2603.22306.

Founder directed: insert A-MBER (the benchmark) into §14.6 in house style,
with parenthetical noting its function. Done — added to make_v081_docx.py,
docx rebuilt, PDF re-exported.

---

## 6. Publish checklists (founder)

### 6.1 GitHub (edm-spec)

All changes are committed on local branch `release/v0.8.1`. Founder steps:

1. Review: `cd edm-spec && git log release/v0.8.1 --oneline -5 && git diff main..release/v0.8.1 --stat`
2. Optionally decide nullable-enum schema fix (candidate #1) — if taken, apply the archived diff, rerun `python releases/v0.8.1/make_v081_docx.py`, re-export PDF, amend the commit.
3. Merge to main: `git checkout main && git merge release/v0.8.1`
4. Tag: `git tag -a v0.8.1 -m "EDM v0.8.1 — references & errata patch. Adds Sofroniew et al. (2026) and Wen et al. (2026, A-MBER) to §14.6; §2.2 mechanistic-evidence sentence; §11.1 and Appendix A errata corrected; nullable-enum errata noted. Zero semantic change; no schema change."`
5. Push: `git push origin main v0.8.1`
6. Create the GitHub release from tag v0.8.1; attach `releases/v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.docx` and `.pdf`.

### 6.2 Zenodo — REUNIFY under concept 10.5281/zenodo.17808652

**Founder decision (2026-06-12):** reunify the lineage under the original
concept DOI 10.5281/zenodo.17808652. The v0.8.1 deposit is created via
"New version" from the latest record in that concept (v0.7.0, record
19211903), NOT as a version of the orphaned 19555166.

1. zenodo.org → My uploads → find the **v0.7.0 record** (10.5281/zenodo.19211903, inside concept 17808652) → **New version**.
2. Upload BOTH files from `edm-spec/releases/v0.8.1/` (docx + pdf).
3. Metadata:
   - Title: "Emotional Data Model (EDM) v0.8.1"
   - Version: "v0.8.1"
   - Publication date: publish date
   - Related identifiers (keep existing + add):
     - `isNewVersionOf 10.5281/zenodo.19211903` (v0.7.0)
     - `isSupplementTo 10.5281/zenodo.19555166` (orphaned v0.8.0 deposit, cross-link)
     - `isDocumentedBy https://emotionaldatamodel.org`
     - `isSupplementedBy` the three GitHub repos
4. Publish; record the new version DOI.
5. **Edit the orphaned v0.8.0 record** (10.5281/zenodo.19555166): add to its
   description a note: "This deposit exists outside the main EDM version
   chain. The unified lineage continues at concept DOI
   10.5281/zenodo.17808652." Add related identifier
   `isObsoletedBy <new v0.8.1 DOI>`.

### 6.3 DOI backfill (after Zenodo assigns the v0.8.1 DOI)

In `edm-spec` (amend or follow-up commit before/after pushing):
- README.md — 5 spots marked `TODO(release)`
- CITATION.cff — 2 spots marked TODO
- docs/RELEASE-NOTES.md — 2 spots marked TODO
- CHANGELOG.md — optionally add the DOI to the 0.8.1 entry

In `emotional_data_model_org` (branch `release/v0.8.1`):
- Replace every `10.5281/zenodo.XXXXXXXX` (MetaStrip, VersionsSection, CitationSection ×2) and update the Zenodo record links (Hero ×2, Downloads, Footer ×2, Navigation, README, llms.txt) from `records/19555166` to the new record. Then merge to main and push — **push deploys** (Vercel).

Elsewhere (proposed, see §1.2): ddna-tools README + llm.txt, deepadata-profile README, deepadata-edm-mcp-server README + llm.txt (npm republish needed for package metadata to update).

### 6.4 Site (already staged)

Branch `release/v0.8.1` @ 9d33828 in `emotional_data_model_org` (unpushed,
build verified). After DOI backfill (§6.3): merge → push → Vercel deploys.
Separately decide the VersionsSection historical-DOI corrections (§1.5).

---

## 7. Recommendation: archive `deepadata-edm-spec`

The folder is a second clone of the same GitHub repo — there is nothing to
archive on GitHub, and **never delete** per instruction. Recommended:

1. Keep `edm-spec` as the only working clone (it is now at origin/main).
2. In the `deepadata-edm-spec` folder: replace README.md with a pointer
   ("This is a retired duplicate clone. Canonical working copy:
   `../edm-spec`; remote: github.com/emotional-data-model/edm-spec") — note
   this README change must NOT be committed/pushed (it would alter the real
   repo); alternatively just drop a `RETIRED-USE-edm-spec.txt` file, which is
   untracked and safe.
3. Move its `.claude/` session context to `edm-spec` if still needed.
4. Separately: `emotionaldatamodel-org-OLD` (a genuinely distinct, superseded
   site repo full of dead `github.com/deepadata/deepadata-edm-spec` links) is
   the thing worth archiving on GitHub if it has a remote.

---

## 8. Out of scope / explicitly not done

- No pushes, no tags, no Zenodo uploads, no npm publishes.
- No schema-file edits (incl. the 24-field nullable fix — staged as diff).
- No crosswalks (none needed — no schema change).
- No pricing-page edit (deepadata-com is platform territory; finding recorded in §3 #4).
- No fixes to other repos' inbound references (proposals only, §1.2).

---

## 9. Decision log

| # | Decision | Date | Source |
|---|---|---|---|
| D1 | **Errata approved**: §11.1 Implementation Profiles attribution corrected v0.8.0→v0.6.0; Appendix A `meta.version` constraint corrected "0.7.x"→"0.8.x" | 2026-06-12 | Founder direction |
| D2 | **A-MBER resolved**: insert the benchmark paper (Wen, Sun, & Wang 2026, arXiv:2604.07017) into §14.6 in house style | 2026-06-12 | Founder direction |
| D3 | **Zenodo lineage reunified**: v0.8.1 deposit via "New version" from v0.7.0 record 19211903 within concept 17808652; orphaned v0.8.0 record 19555166 cross-linked | 2026-06-12 | Founder direction |
| D4 | **Misuse and Dual-Use Considerations**: added as v0.9 candidate (candidate #11) — normative framing of visibility/masking_rules/pii_tier/consent as anti-manipulation controls | 2026-06-12 | Founder direction |
| D5 | **Commit on release/v0.8.1**: all changes committed locally, no push, no tag — founder publishes | 2026-06-12 | Founder direction |

---

## 10. Founder execution checklist (one screen)

At the next sitting, in order:

1. **Review the commit:**
   ```
   cd edm-spec
   git log release/v0.8.1 --oneline -3
   git diff main..release/v0.8.1 --stat
   ```

2. **Optional: nullable-enum schema fix** (candidate #1) — if desired,
   apply the archived diff from `pending/`, rerun `python
   releases/v0.8.1/make_v081_docx.py`, re-export PDF, amend the commit.

3. **Merge to main and tag:**
   ```
   git checkout main
   git merge release/v0.8.1
   git tag -a v0.8.1 -m "EDM v0.8.1 — references & errata patch"
   git push origin main v0.8.1
   ```

4. **GitHub release:** create from tag v0.8.1; attach the docx + pdf
   from `releases/v0.8.1/`.

5. **Zenodo deposit (reunified):**
   - Go to the v0.7.0 record (19211903) → "New version"
   - Upload docx + pdf from `releases/v0.8.1/`
   - Set title/version/date; add related identifiers per §6.2
   - Publish → record the new version DOI

6. **Edit orphaned v0.8.0 record** (19555166): add description note
   pointing to unified lineage at concept 17808652.

7. **DOI backfill** (§6.3): replace `TODO(release)` placeholders in
   README.md (×5), CITATION.cff (×2), RELEASE-NOTES.md (×2) with the
   new version DOI. Commit and push.

8. **Site deploy** (`emotional_data_model_org`): backfill DOI in branch
   `release/v0.8.1`, merge to main, push (Vercel deploys on push).

9. **Downstream DOI updates** (optional): ddna-tools, mcp-server,
   deepadata-profile README/llm.txt.
