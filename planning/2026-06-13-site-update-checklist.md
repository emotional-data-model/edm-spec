# emotional_data_model_org — v0.8.1 Update Checklist

**Prepared:** 2026-06-13
**Applies after:** v0.8.1 Zenodo DOI is assigned and edm-spec is tagged/pushed.
**Branch:** `release/v0.8.1` (commit 9d33828, already staged but DOIs are placeholders).
**Deploy mechanism:** Vercel Git integration — pushing to production branch publishes the site.

---

## 1. DOI backfill (blocking — do before push)

Replace every `10.5281/zenodo.XXXXXXXX` placeholder with the actual v0.8.1 version DOI:

| File | Locations |
|------|-----------|
| `src/components/MetaStrip.tsx` | DOI display string (1 instance) |
| `src/components/sections/CitationSection.tsx` | citation string + bibtex doi field (2 instances) |
| `src/components/sections/VersionsSection.tsx` | v0.8.1 row doi property (1 instance) |

Also update Zenodo record URLs from `records/19555166` to the new record number:

| File | Locations |
|------|-----------|
| `src/components/sections/HeroSection.tsx` | Zenodo link (2 instances) |
| `src/components/sections/DownloadsSection.tsx` | Download href (1 instance) |
| `src/components/Navigation.tsx` | If Zenodo link exists |
| `public/llms.txt` | Zenodo reference if present |
| `README.md` | DOI/Zenodo references |

## 2. Version strings (already staged on release/v0.8.1)

These are done in commit 9d33828 — verify they survived any rebase:

| File | Change |
|------|--------|
| `src/components/Navigation.tsx` | `v0.8.0` → `v0.8.1` |
| `src/components/MetaStrip.tsx` | version `v0.8.0` → `v0.8.1`, date `March 2026` → `June 2026` |
| `src/components/sections/HeroSection.tsx` | `v0.8.0` → `v0.8.1` (2 instances) |
| `src/components/sections/DownloadsSection.tsx` | `v0.8.0 · 96 pp` → `v0.8.1 · 91 pp` |
| `src/components/sections/VersionsSection.tsx` | v0.8.1 row added as current, v0.8.0 archived |
| `src/components/sections/CitationSection.tsx` | version `v0.8.0` → `v0.8.1` (citation + bibtex) |
| `public/llms.txt` | `v0.8.0 (April 2026)` → `v0.8.1 (June 2026)` |

## 3. Additional files to update (not yet staged)

| File | Change |
|------|--------|
| `README.md` | line ~13: `v0.8.0 (April 2026)` → `v0.8.1 (June 2026)` |
| `CLAUDE.md` | line ~15: current version `v0.8.0` → `v0.8.1` |
| `index.html` | line ~7: meta description `v0.8.0` → `v0.8.1` |

## 4. Changelog entry

`VersionsSection.tsx` — the v0.8.1 row notes field should read:
> "References & errata patch — Sofroniew et al. (2026), Wen et al. (2026, A-MBER) added to §14.6; nullable-enum schema correction per §5.2; zero semantic change"

## 5. Fabricated-DOI corrections (founder queue item 9)

The historical version table in `VersionsSection.tsx` contains fabricated DOIs
for v0.7.0 and earlier (15243817, 14992765, 14205103, 14002003 — none exist on
Zenodo). Correct these to the real DOIs from the authoritative lineage:

| Version | Fabricated DOI | Real DOI |
|---------|---------------|----------|
| v0.7.0 | 15243817 | 10.5281/zenodo.19211903 |
| v0.6.0 | 14992765 | 10.5281/zenodo.18951891 |
| v0.5.0 | 14205103 | 10.5281/zenodo.18541956 |
| v0.4.0 | 14002003 | 10.5281/zenodo.17808653 |

Also add missing v0.5.1 row (DOI: 10.5281/zenodo.18883392, March 2026) and
correct any wrong dates/notes per HANDOFF §1.4 and §1.5.

## 6. Deploy sequence

1. Complete DOI backfill (§1) and additional file updates (§3)
2. Verify build: `npm run build`
3. Merge `release/v0.8.1` to main
4. Push to origin — Vercel deploys automatically
5. Verify live site shows v0.8.1, correct DOI, correct download link
