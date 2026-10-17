# EDM vocabulary namespace stub (proposed, v1)

Discovery output, 2026-10-17. The namespace `https://emotionaldatamodel.org/vocab/` does **not** resolve yet. This folder is the proposal for what it would serve.

| File | What it is |
|---|---|
| `edm-vocab-v1.ttl` | SKOS (Turtle) for seven v0.9 vocabularies: `arc`, `tether`, `relationship`, `memory_type`, `temporal_profile`, `need`, `coping`. One `skos:ConceptScheme` per vocabulary, one `skos:Concept` per canonical value, and one `skos:exactMatch` / `broadMatch` / `narrowMatch` / `relatedMatch` triple per crosswalk cell, generated from `../crosswalk.csv` by `../scripts/skos_build.py`. |

Conventions:

- Concept URI: `https://emotionaldatamodel.org/vocab/<field>/v1#<value>`. The fragment is the exact v0.8.3 value string, so an artifact's `text` is also its EDM code.
- Relation mapping: crosswalk `exact` → `skos:exactMatch`, `broader` → `skos:broadMatch`, `narrower` → `skos:narrowMatch`, `related` → `skos:relatedMatch`. Direction is EDM → target, as in the crosswalk.
- Targets with a published URI use it (MFOEM classes as OBO PURLs). Frameworks that publish no concept URIs (Booker, Campbell, McAdams, Lazarus, Pillemer, SDT, Fiske, Bronfenbrenner, EmotionML vocabulary items, and the rest) get a **placeholder** concept under `https://emotionaldatamodel.org/xref/v1/<framework_id>#<slug>`, labelled with the crosswalk's target text, sourced to the framework's citation URL, and annotated with the crosswalk verification flag (V / K / -). Placeholders are to be replaced by authoritative URIs if the framework ever publishes them; they are not claims of ownership.
- Values deprecated in the v0.9 proposal carry `owl:deprecated true`, a `skos:note` with the reason, and `dcterms:isReplacedBy` where a canonical replacement exists. They remain valid `text`.
- Values with no framework mapping carry `skos:note "orphan ..."`; these are the EDM-specific constructs listed in `../REPORT.md` §4.

Regenerate:

```
python -I scripts/skos_build.py crosswalk.csv frameworks.json vocab/edm-vocab-v1.ttl
```

Validate (any Turtle parser; rdflib was used for this commit):

```
python -c "import rdflib; g=rdflib.Graph(); g.parse('vocab/edm-vocab-v1.ttl', format='turtle'); print(len(g))"
```

Not yet covered (same mechanism, follow-up): `emotion`, `life_stage`, `scope`, `recurrence`, `persistence`, `trajectory`, `action_tendency`, `temporal_focus`, `risk_posture`, `urgency`, `control`, `valence`, and the opt-in trait vocabularies `attachment_style`, `regulation_state`. The migration script in `../scripts/v09_layout.py` already mints codes in those namespaces for canonical values.
