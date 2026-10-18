# Schema sketch — per-field `evidence` and the `reading` block (additive, migration-neutral)

**Discovery note, 2026-10-18. Not normative; not part of the draft schema build (`draft-schema/` is generated and untouched).** The JSON Schema draft is `reading.fragment.json` beside this file; this note says what it is for, why it is shaped as it is, and what it does not do.

## 1. What is added

One optional top-level infrastructure object, `reading`, with three members:

| Member | Shape | Purpose |
|---|---|---|
| `reading.source` | `{sha256, length, normalisation, turns?}` | Pins the text the offsets index: sha256 and code-point length of the NFC-normalised, LF-ended text. Optional turn index (speaker, span, timestamp) for conversational sources so turn-level cues can be checked. |
| `reading.evidence` | `{ "<field path>": [ {span, quote, role?, extractor?} ... ] }` | **Per field:** the span(s) the populated value is attributable to. `quote` must equal the text at `span`; `role` says whether the value is *stated* in the span, *interpreted* from it, or whether the span is a *contrast* / *status* span a cue needs. |
| `reading.readings` | `[ {cues[], spans[], field, label_licensed, licence, norm?, flags[], extractor, populated?} ... ]` | **The reading block:** cue codes from `cues-v1.md`, the span(s) the cue rests on, the field it points at, the label it licenses, how strongly (`pointer` / `hypothesis` / `candidate`), the norm it departs from, flags, which extractor read it, and whether the field's value took it up. |

Keyed by dotted field path, as `telemetry.field_confidence` already is, so **no affective fragment changes**: a string field such as `narrative.harm` (which cannot carry a member) and a coded object such as `emotion.primary` are handled the same way, from outside.

## 2. Why additive and outside the fields

- **Migration-neutral.** A v0.8.3 artifact migrated by `v09_layout.py` has no `reading` and is valid; a v0.9 artifact with `reading` is valid against every profile because the key is optional at the top level and absent from `required`. The draft composites set `additionalProperties: false` at the top level, so admitting the key is a one-line addition to each composite (`"reading": {"$ref": ".../fragments/reading.json"}`) when a ruling takes it; until then the fragment lives here.
- **Nothing in the affective domains changes meaning.** A consumer that ignores `reading` reads the same artifact as before. A field's value is never *defined* by its reading; the field rule (interpretation attributable to a passage) still populates it. The block makes the passage findable and the licence inspectable.
- **Seal hash.** Telemetry is excluded from the seal hash (v0.8.x). Evidence spans are a provenance claim about the sealed values and arguably belong *inside* the seal; this sketch leaves `reading` with telemetry (unsealed) and flags the question for the founder: sealing `reading.evidence` would make an artifact's attribution verifiable, at the cost that re-extraction with a different model changes the seal even when every value is identical. Recommended: seal `evidence`, leave `readings` unsealed; not decided here.
- **Privacy.** `evidence.quote` repeats source text inside the artifact. For a journal that is the owner's own text; for a conversation it may be another party's words. The `pii_tier` and `visibility` rules of `meta` apply to quotes exactly as to `narrative.summary`; a profile that forbids verbatim source text (none does today) would set `evidence` to spans without quotes, which the fragment permits by making `quote` required only because verification needs it — a `quote: ""` with `role: "stated"` is a documented degradation, not an error. This needs a ruling before any product use.

## 3. The per-field `evidence` rule

For every populated affective field in the artifact, zero or more evidence spans. The rule proposed for run 4 and for any future extraction prompt:

1. **Stated** fields (`self_position`, `bodily_sensation`, `appraisal.attribution`, `turning_point`, `function`, and any coded field read from the text's own word): exactly one span whose text contains the value's word or its unmistakable paraphrase; `role: "stated"`.
2. **Interpreted** fields (everything else that is populated): one to three spans that together support the interpretation; `role: "interpreted"`. More than three is a sign the field is being read from the whole text, which is what `narrative.summary` is for.
3. **A field with no span is a field with no basis.** The null rule of every field already says that; the evidence rule makes it checkable: a populated field without an evidence entry is flagged by the validator (warning in draft, error if a profile adopts the rule).
4. **Offsets are verifiable.** `quote == text[start:end]` after the stated normalisation, and `sha256(text) == reading.source.sha256`. A validator that has the text checks both; one that does not marks the spans unverified. The run-4 scorer (`experiment-plan-run4.md` §5) treats a failed check as a missing span for that extractor.

## 4. The `reading` block

A reading is *a cue, where it is, and what it licenses*. Its members follow the catalogue's rules (`cues-v1.md` §9):

- `cues`: one or more codes. Two cues on the same referent raise the licence from `hypothesis` to `candidate`.
- `spans`: the span(s) the cue rests on, with the role of each (`contrast` for the weighted span a minimiser is read against; `status` for the span that states a person is dead when a tense shift is read). A pair cue carries two spans; `rl:absent-party` carries the scene span and an empty second span (`end == start`).
- `field` and `label_licensed`: which field the cue points at and with what value, in the field's value words; `null` when the cue only says *this is where the field's referent is* (`licence: "pointer"`).
- `norm`: the departure the cue names, instantiated for this text ("the writer's other replies in this thread arrive within two minutes"; "Dad is stated dead at 0–14"). A reading without a norm is not a reading.
- `flags`: `typo_risk` on every slip; `unscorable` when a comparative or timestamped cue lacks its baseline; `negated` on unasked denials; `model_authored_risk` where the span may be model-written (companion arm); `comparative` for rate-based cues.
- `extractor`: which model read it; **`populated`: whether the field's value equals the licensed label**, recorded from the artifact, never inferred. This is the hook for the cue → label stability measure in run 4.

A `reading` never populates a field. The extractor that proposes a `candidate` for `narrative.subject` still has to populate `narrative.subject` under the field rule, and the `evidence` entry for `narrative.subject` then says which span it rests on. The two blocks can disagree (a reading proposes, the field says otherwise); that disagreement is data, not an error.

## 5. Worked example (synthetic)

Source text (normalised; offsets are code points):

```
Dad died in March. He's always on at me about the car. I should sort the car. Anyway.
```

`0–18` "Dad died in March." · `19–54` "He's always on at me about the car." · `55–78` "I should sort the car." · `79–86` "Anyway."

```json
{
  "narrative": {"harm": "dad", "integration": null, "summary": "..."},
  "salience": {"tether": {"type": {"text": "person"}, "referent": "dad", "stake": null}},
  "emotion": {"primary": {"text": "sadness"}, "temporal_profile": {"text": "ongoing"}},
  "reading": {
    "cue_vocabulary": "https://emotionaldatamodel.org/vocab/cues/v1",
    "source": {"sha256": "<sha256 of the normalised text>", "length": 86, "normalisation": "nfc-lf"},
    "evidence": {
      "narrative.harm": [{"span": {"start": 0, "end": 18}, "quote": "Dad died in March.", "role": "stated"}],
      "salience.tether.type": [{"span": {"start": 19, "end": 54}, "quote": "He's always on at me about the car.", "role": "interpreted"}],
      "emotion.primary": [{"span": {"start": 0, "end": 18}, "quote": "Dad died in March.", "role": "interpreted"}],
      "emotion.temporal_profile": [{"span": {"start": 19, "end": 54}, "quote": "He's always on at me about the car.", "role": "interpreted"},
                                   {"span": {"start": 79, "end": 86}, "quote": "Anyway.", "role": "interpreted"}]
    },
    "readings": [
      {"cues": ["rl:tense-shift-person"], "field": "salience.tether.type", "label_licensed": "person", "licence": "hypothesis",
       "spans": [{"span": {"start": 19, "end": 54}, "quote": "He's always on at me about the car.", "role": "interpreted"},
                 {"span": {"start": 0, "end": 18}, "quote": "Dad died in March.", "role": "status"}],
       "norm": "Dad is stated dead at 0-18; the present tense at 19-54 departs from that status", "flags": [], "extractor": "claude-sonnet-5-5", "populated": true},
      {"cues": ["rl:tense-shift-person", "rl:repetition"], "field": "narrative.subject", "label_licensed": "the car", "licence": "candidate",
       "spans": [{"span": {"start": 19, "end": 54}, "quote": "He's always on at me about the car.", "role": "interpreted"},
                 {"span": {"start": 55, "end": 78}, "quote": "I should sort the car.", "role": "interpreted"}],
       "norm": "the car is named in both of the two sentences after the death; nothing else is", "flags": [], "extractor": "claude-sonnet-5-5", "populated": false},
      {"cues": ["rl:open-coda"], "field": "narrative.integration", "label_licensed": null, "licence": "pointer",
       "spans": [{"span": {"start": 79, "end": 86}, "quote": "Anyway.", "role": "interpreted"}],
       "norm": "a coda that returns the teller to the present; this one closes nothing", "flags": [], "extractor": "claude-sonnet-5-5", "populated": false}
    ]
  }
}
```

The `emotion.primary` value `sadness` is interpreted from the stated death, not from the tense shift: the reading block has no entry licensing `emotion.primary` (the catalogue says the tense cue does not license it), and the evidence entry says where it was read from. The second reading proposes `the car` as `narrative.subject`; the field was left null by the extractor (`populated: false`); run 4 scores whether other extractors made the same proposal and the same choice.

## 6. What this sketch does not do

- It does not add a field, a value, a domain or a profile member; Essential 18 / Extended 28 / Full 47 are unchanged.
- It does not change `telemetry`, `governance` or `meta`.
- It does not make `reading` required anywhere, nor decide the seal question (§2), nor the quote-privacy question (§2).
- It does not fix the offset convention beyond NFC + LF code points; a product that stores text differently must record its own normalisation.
- It is not validated against any example; `migrated-examples/` carry no `reading` block. Run 4 produces the first artifacts that would.

## 7. Open questions for the founder

1. Admit `reading` to the draft composites (one line each) so run 4's outputs validate, or keep it a sidecar until the experiment reports.
2. Seal `evidence`, `readings`, both, or neither.
3. Whether `quote` may be omitted under a privacy profile, and if so what the validator requires instead.
4. Whether the cue vocabulary becomes a SKOS scheme beside `edm-vocab-v1.ttl` (the catalogue is shaped for it: code, definition, lineage as `skos:note`, licence as a typed relation) or stays a discovery document.
