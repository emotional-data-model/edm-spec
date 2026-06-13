# Builds releases/v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.docx from the
# v0.8.0 docx by applying only the v0.8.1 patch edits (references + errata +
# version metadata). Emits an audit log of every changed paragraph.
import zipfile, re, shutil, sys, html

SRC = "releases/v0.8.0/EDM_v0_8_0_Whitepaper_Harvey_2026.docx"
DST = "releases/v0.8.1/EDM_v0_8_1_Whitepaper_Harvey_2026.docx"

S22_SENTENCE = (
    " Recent interpretability work (Sofroniew et al., 2026) provides direct "
    "mechanistic evidence for this position: model-internal emotion "
    "representations are real, causally influence behaviour, and leave no "
    "trace in output text — confirming that affective context cannot be "
    "governed at the output layer."
)

LINEAGE_PARA = (
    "v0.8.1 is a patch release containing references and errata only, with "
    "zero semantic change. Section 14.6 adds Sofroniew et al. (2026), "
    "mechanistic interpretability evidence that model-internal emotion "
    "representations causally influence model behaviour while remaining "
    "invisible in output text, and Wen, Sun, & Wang (2026), the A-MBER "
    "benchmark for evaluating affective memory in AI systems; Section 2.2 "
    "records the Sofroniew evidence. Errata: Section 11.1 corrects the "
    "attribution of Implementation Profiles from v0.8.0 to v0.6.0; "
    "Appendix A corrects the meta.version constraint from \"0.7.x\" to "
    "\"0.8.x\"; the reference-schema nullable-enum correction (twenty-four "
    "fields across Constellation, Gravity, Impulse, and Milky_Way) is "
    "recorded in CHANGELOG.md. No schema structures, field semantics, "
    "or enumeration values are added, modified, or removed."
)

SOFRONIEW_REF = (
    "Sofroniew, N., Kauvar, I., Saunders, W., Chen, R., et al. (2026). "
    "Emotion Concepts and their Function in a Large Language Model. "
    "Anthropic, Transformer Circuits. arXiv:2604.07729. (Mechanistic "
    "evidence that affective context causally influences model behaviour "
    "while remaining invisible in outputs)."
)

AMBER_REF = (
    "Wen, D., Sun, K., & Wang, Y. (2026). A-MBER: Affective Memory "
    "Benchmark for Emotion Recognition. arXiv:2604.07017. (Benchmark "
    "for evaluating affective/emotional memory in AI systems)."
)

# paragraph-index -> list of (old, new) string replacements applied run-wise
REPLACEMENTS = {
    0:   [("v0.8.0", "v0.8.1")],
    2:   [("v0.8.0", "v0.8.1")],
    3:   [("March 2026", "June 2026")],
    6:   [("10.5281/zenodo.19555166",
          "pending — assigned on Zenodo publication "
          "(v0.8.0: 10.5281/zenodo.19555166)")],
    19:  [("v0.8.0", "v0.8.1")],   # split across runs; handled specially
    25:  [("v0.8.0", "v0.8.1")],
    34:  [("v0.8.0", "v0.8.1")],
    37:  [("v0.8.0", "v0.8.1")],
    50:  [("v0.8.0", "v0.8.1")],
    128: [("v0.8.0", "v0.8.1")],
    132: [("v0.8.0", "v0.8.1")],
    196: [("v0.8.0", "v0.8.1")],
    197: [("v0.8.0", "v0.8.1")],
    226: [("v0.8.0", "v0.8.1")],
    327: [("v0.8.0", "v0.8.1")],
    355: [("v0.8.0", "v0.8.1")],
    361: [("v0.8.0)", "v0.8.0 → v0.8.1)")],
    362: [("v0.8.0 introduces Implementation Profiles",
           "v0.6.0 introduces Implementation Profiles")],
    381: [("v0.8.0", "v0.8.1")],
    439: [('"0.7.x"', '"0.8.x"')],
}
APPEND_TO = {46: S22_SENTENCE}
INSERT_AFTER = {364: [LINEAGE_PARA], 428: [SOFRONIEW_REF, AMBER_REF]}

P_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)
T_RE = re.compile(r"(<w:t[^>]*>)(.*?)(</w:t>)", re.S)

def para_text(p):
    return "".join(m[1] for m in T_RE.findall(p))

def replace_in_para(p, old, new):
    """Replace old->new inside a paragraph, run-wise; fall back to merging
    all run text into the first run if the match spans runs."""
    done = [False]
    def sub(m):
        if not done[0] and old in m.group(2):
            done[0] = True
            return m.group(1) + m.group(2).replace(old, new, 1) + m.group(3)
        return m.group(0)
    out = T_RE.sub(sub, p)
    if done[0]:
        return out
    # cross-run: merge all text into the first w:t, blank the rest
    full = para_text(p)
    assert old in full, f"target not found: {old!r} in {full[:80]!r}"
    merged = full.replace(old, new, 1)
    first = [True]
    def sub2(m):
        if first[0]:
            first[0] = False
            return (m.group(1).replace("<w:t>", '<w:t xml:space="preserve">')
                    if 'xml:space' not in m.group(1)
                    else m.group(1)) + html.escape(merged, quote=False) + m.group(3)
        return m.group(1) + m.group(3)
    return T_RE.sub(sub2, p)

def append_to_para(p, text):
    ts = list(T_RE.finditer(p))
    assert ts, "no runs in paragraph"
    last = ts[-1]
    opener = last.group(1)
    if "xml:space" not in opener:
        opener = opener.replace("<w:t", '<w:t xml:space="preserve"', 1)
    new_seg = opener + last.group(2) + html.escape(text, quote=False) + last.group(3)
    return p[:last.start()] + new_seg + p[last.end():]

def clone_para(p, text):
    """New paragraph using p's paragraph + first-run properties."""
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
        p = replace_in_para(p, old, new)
    new_paras[idx] = p
    audit.append((idx, "REPLACE", before, para_text(p)))

for idx, text in APPEND_TO.items():
    p = new_paras.get(idx, paras[idx])
    before = para_text(p)
    p = append_to_para(p, text)
    new_paras[idx] = p
    audit.append((idx, "APPEND", before, para_text(p)))

inserts = {}  # idx -> xml to insert after
for idx, texts in INSERT_AFTER.items():
    inserts[idx] = "".join(clone_para(paras[idx], t) for t in texts)
    for t in texts:
        audit.append((idx, "INSERT-AFTER", "(n/a)", t))

# rebuild document.xml back-to-front so spans stay valid
out = xml
for idx in sorted(set(list(new_paras) + list(inserts)), reverse=True):
    s, e = spans[idx]
    rep = new_paras.get(idx, paras[idx])
    if idx in inserts:
        rep = rep + inserts[idx]
    out = out[:s] + rep + out[e:]

new_header = header.replace(">v0.8.0<", ">v0.8.1<")
assert new_header != header, "header replacement failed"

# write the new docx
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
print(f"HEADER: 'EDM v0.8.0' -> 'EDM v0.8.1'")
for idx, kind, before, after in sorted(audit):
    print(f"\n--- para {idx} [{kind}] ---")
    print("BEFORE:", before[:300])
    print("AFTER :", after[:300] if kind != "INSERT-AFTER" else after[:400])
