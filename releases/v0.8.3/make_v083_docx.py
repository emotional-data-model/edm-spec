# Builds releases/v0.8.3/EDM_v0_8_3_Whitepaper_Harvey_2026.docx from the
# v0.8.1 docx by applying the v0.8.2 + v0.8.3 truth edits:
#   - current-version references v0.8.1 -> v0.8.3; date; DOI placeholder
#   - Appendix A narrative_archetype: 12 identity archetypes,
#     identity-not-role definition (ADR-0030); ditto Section 4 prose + glossary
#   - Full profile field count 96 -> 91 (Artifact B4 line)
#   - source_timestamp attribution corrected to v0.7.0 (crosswalks as truth);
#     extraction_chunking_strategy removal attribution corrected to v0.7.0
#   - Section 11.1 lineage: title extended; v0.8.2 + v0.8.3 paragraphs
#     inserted; carried v0.8.1 erratum applied ("v0.8.0 introduces
#     Implementation Profiles" -> v0.6.0 — the 0.8.1 build recorded this fix
#     in its CHANGELOG but the archived docx does not carry it)
#   - Appendix B example version stamps corrected 0.6.0 -> 0.8.3
# Emits an audit log of every changed paragraph.
import zipfile, re, shutil, sys, html

SRC = "releases/v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.docx"
DST = "releases/v0.8.3/EDM_v0_8_3_Whitepaper_Harvey_2026.docx"

V082_PARA = (
    "v0.8.2 is a schema-reconciliation patch that brings the published JSON "
    "Schema fragments into alignment with the canonical vocabulary (ADR-0030: "
    "the published specification is the source of truth and downstream "
    "implementations generate from it). The narrative_archetype enumeration "
    "is corrected to the twelve canonical identity archetypes — hero, "
    "caregiver, seeker, sage, lover, outlaw, innocent, magician, creator, "
    "everyman, jester, ruler. The field encodes the archetypal identity the "
    "subject embodies, not a structural role or literary trope: mentor is "
    "removed from the fragment enumeration on this ground, and orphan, which "
    "earlier documents listed but no shipped v0.8 fragment enumerated, is "
    "likewise outside the canonical set. motivational_orientation gains "
    "authenticity (self-alignment and identity congruence), aligning the "
    "fragment with the canonical vocabulary. The shared meta.profile fragment "
    "is reconciled to the two-tier model (canonical enumeration plus the "
    "partner: pattern), and a mis-encoded enumeration on meta.tags is "
    "removed. A non-validating x-edm-canonical annotation is added to seven "
    "two-tier free-text fields, carrying the preferred canonical vocabulary "
    "in machine-readable form. The specification is published to npm "
    "(edm-spec@0.8.2). No fields are added, removed, or renamed. v0.8.2 "
    "shipped without a standalone document; its changes are documented in "
    "the v0.8.1-to-v0.8.2 crosswalk and folded into this v0.8.3 document."
)

V083_PARA = (
    "v0.8.3 is a truth-only patch release. The Full Profile composite schema "
    "gains meta.source_timestamp in its inline meta block, conforming to the "
    "canonical meta fragment: the field, added in v0.7.0, had been "
    "strict-rejected by the composite's additionalProperties constraint "
    "since v0.8.0. The change is strictly widening — every artifact valid "
    "under v0.8.2 remains valid, and Full Profile artifacts carrying "
    "meta.source_timestamp now validate as the fragment always intended. The "
    "Full Profile field count is corrected to 91, the machine count of "
    "top-level fields across the ten domains of the shipped composite; the "
    "prior figure of 96 was hand arithmetic that never matched a shipped "
    "v0.8 schema. The narrative_archetype description is corrected to the "
    "identity-archetype definition throughout this document; the enumeration "
    "is unchanged at twelve. A one-story release policy is adopted "
    "(docs/RELEASE-POLICY.md): every npm release must have its document "
    "staged, npm and Zenodo publication occur together, and no certification "
    "claim may cite a version whose document is not published. No fields are "
    "introduced, deprecated, or semantically modified beyond the composite "
    "conformance correction."
)

VBUMP = [("v0.8.1", "v0.8.3")]

# paragraph-index -> list of (old, new) replacements, applied replace-ALL
REPLACEMENTS = {
    0:    VBUMP,                       # title
    2:    VBUMP,                       # Version:
    3:    [("June 2026", "July 2026")],
    6:    [("10.5281/zenodo.20678017",
            "pending — assigned on Zenodo publication "
            "(v0.8.1: 10.5281/zenodo.20678017)")],
    8:    VBUMP,   # abstract
    19:   VBUMP,
    25:   VBUMP,   # section 1 heading
    34:   VBUMP,
    37:   VBUMP,
    41:   VBUMP,
    44:   VBUMP,
    50:   VBUMP,
    120:  [("0.8.1", "0.8.3")],        # edm_version example
    128:  VBUMP,
    196:  VBUMP,   # section 4 heading
    197:  VBUMP,
    213:  [("structural role via the narrative_archetype, defining their "
            "position within the story geometry",
            "archetypal identity via the narrative_archetype — which of the "
            "twelve canonical identity archetypes the subject embodies, an "
            "identity rather than a structural role")],
    226:  VBUMP,
    234:  VBUMP,
    310:  VBUMP,
    327:  VBUMP,
    343:  VBUMP,
    355:  VBUMP,
    361:  [("v0.8.1)", "v0.8.1 → v0.8.2 → v0.8.3)")],   # 11.1 title
    362:  [("v0.8.0 introduces Implementation Profiles",
            "v0.6.0 introduces Implementation Profiles")],  # carried erratum
    382:  VBUMP,
    433:  VBUMP,   # Appendix A title
    501:  [("Added in v0.8.0.", "Added in v0.7.0.")],   # source_timestamp
    575:  [("The structural role or literary trope the subject occupies "
            "within the narrative.",
            "The archetypal identity the subject embodies — which of the 12 "
            "canonical identity archetypes the subject expresses, not a "
            "structural role or story function.")],
    576:  [("hero, caregiver, seeker, sage, lover, outlaw, innocent, "
            "magician, creator, everyman, jester, ruler, mentor, orphan.",
            "hero, caregiver, seeker, sage, lover, outlaw, innocent, "
            "magician, creator, everyman, jester, ruler.")],
    607:  [("Added in v0.8.0.", "Added in v0.7.0.")],   # arc_type (crosswalk)
    823:  [("Added in v0.8.0.", "Added in v0.7.0.")],   # extensions (crosswalk)
    807:  [("removed from Telemetry in v0.8.1",
            "removed from Telemetry in v0.7.0")],
    846:  VBUMP,   # Appendix B title
    855:  [('"0.6.0"', '"0.8.3"')],    # example B1 version stamp
    904:  [('"0.6.0"', '"0.8.3"')],    # example B2 version stamp
    985:  [('"0.6.0"', '"0.8.3"')],    # example B3 version stamp
    1147: [("Full (96 fields extracted and stored)",
            "Full (91 fields extracted and stored)")],
    1151: [('"0.8.1"', '"0.8.3"')],    # example B4 version stamp
    1201: VBUMP,
    1206: [('"0.6.0"', '"0.8.3"')],    # envelope example edm_version stamp
    1217: [("edm.v0.8.1", "edm.v0.8.3")],
    1229: [('"0.6.0"', '"0.8.3"')],    # envelope example version stamp
    1265: [('"0.6.0"', '"0.8.3"')],    # edm_version field description e.g.
    1286: [("edm.v0.8.1", "edm.v0.8.3")],
    1456: VBUMP,
    1462: VBUMP,
    1522: [("assigning structural role (hero, seeker, caregiver, sage, "
            "etc.).",
            "assigning the archetypal identity the subject embodies (hero, "
            "seeker, caregiver, sage, etc.); an identity, not a structural "
            "role.")],
}
INSERT_AFTER = {365: [V082_PARA, V083_PARA]}

P_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)
T_RE = re.compile(r"(<w:t[^>]*>)(.*?)(</w:t>)", re.S)

def para_text(p):
    return "".join(m[1] for m in T_RE.findall(p))

def replace_all_in_para(p, old, new):
    """Replace every occurrence of old with new. Run-wise when each
    occurrence sits inside a single run; otherwise merge all run text into
    the first run."""
    full = para_text(p)
    assert old in full, f"target not found: {old!r} in {full[:120]!r}"
    # try run-wise first (covers the common case)
    def sub(m):
        if old in m.group(2):
            return m.group(1) + m.group(2).replace(old, new) + m.group(3)
        return m.group(0)
    out = T_RE.sub(sub, p)
    if old not in para_text(out) or para_text(out).count(old) < full.count(old):
        if old not in para_text(out):
            return out
    # cross-run fallback: merge everything into the first w:t
    merged = full.replace(old, new)
    first = [True]
    def sub2(m):
        if first[0]:
            first[0] = False
            opener = m.group(1)
            if "xml:space" not in opener:
                opener = opener.replace("<w:t", '<w:t xml:space="preserve"', 1)
            return opener + html.escape(merged, quote=False) + m.group(3)
        return m.group(1) + m.group(3)
    return T_RE.sub(sub2, p)

def clone_para(p, text):
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
    rpr = re.search(r"<w:rPr>.*?</w:rPr>", p, re.S)
    return ("<w:p>" + (ppr.group(0) if ppr else "")
            + "<w:r>" + (rpr.group(0) if rpr else "")
            + '<w:t xml:space="preserve">' + html.escape(text, quote=False)
            + "</w:t></w:r></w:p>")

shutil.copy(SRC, DST)
zin = zipfile.ZipFile(SRC)
xml = zin.read("word/document.xml").decode("utf-8")
header = zin.read("word/header1.xml").decode("utf-8")

paras = P_RE.findall(xml)
spans = [m.span() for m in P_RE.finditer(xml)]
audit = []

new_paras = {}
for idx, reps in REPLACEMENTS.items():
    p = paras[idx]
    before = para_text(p)
    for old, new in reps:
        p = replace_all_in_para(p, old, new)
    new_paras[idx] = p
    audit.append((idx, "REPLACE", before, para_text(p)))

inserts = {}
for idx, texts in INSERT_AFTER.items():
    inserts[idx] = "".join(clone_para(paras[idx], t) for t in texts)
    for t in texts:
        audit.append((idx, "INSERT-AFTER", "(n/a)", t))

out = xml
for idx in sorted(set(list(new_paras) + list(inserts)), reverse=True):
    s, e = spans[idx]
    rep = new_paras.get(idx, paras[idx])
    if idx in inserts:
        rep = rep + inserts[idx]
    out = out[:s] + rep + out[e:]

new_header = header.replace("v0.8.1", "v0.8.3")
assert new_header != header, "header replacement failed"

zout = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename == "word/document.xml":
        data = out.encode("utf-8")
    elif item.filename == "word/header1.xml":
        data = new_header.encode("utf-8")
    zout.writestr(item, data)
zout.close()

sys.stdout.reconfigure(encoding="utf-8")
print(f"WROTE {DST}")
print("HEADER: 'EDM v0.8.1' -> 'EDM v0.8.3'")
for idx, kind, before, after in sorted(audit):
    print(f"\n--- para {idx} [{kind}] ---")
    print("BEFORE:", before[:300])
    print("AFTER :", after[:300] if kind != "INSERT-AFTER" else after[:400])
