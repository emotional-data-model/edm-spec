# Vision

Read this first. It states what EDM is for and the test of success.

## What EDM is

An open, machine-portable record of what a text says about feeling,
significance and motivation. The person's own words stay as text; codes
sit beneath them; evidence spans and extractor provenance ride with every
reading; governance (consent, retention, rights) is in the record.

Representation before computation: the record exists so that memory,
companion and therapy systems can carry affective context across models
and across time without inferring beyond the text.

## What is new in the LLM era

The reader is a model, the medium is text-only and timestamped, and the
reading can be written down and compared. The labels are old (crosswalked
to 39 frameworks, MFOEM, EmotionML). The signs are old (Darwin, Goffman,
Grice, conversation analysis). The reading layer, unsaid cues mapped to
labels with evidence and recorded with provenance, is the contribution.

EDM captures what matters to an individual beyond a model's pretraining,
so that it can be interpreted by future models and by other vendors.

The reading is explicit, not inferred: not what a model read, which is
unknowable, but what it reports having read, with the span it points to,
so that a reading can be checked and compared across models — agreement
makes a reading more credible, never certain.

EDM is an LLM-first, open-source emotional and affective context
framework, complete with its predecessors through the crosswalks, and
portable.

## Design principles earned by evidence

From runs 1–3 and anchors 1–2 (October 2026):

- Quotation beats interpretation for portability.
- Numbers beat ordinals for gradients.
- Recommended vocabulary beats enums.
- Widening a vocabulary relocates agreement rather than adding it, so
  text plus codings at several grains is mandatory.
- Profiles are derived from measured comparability, not chosen.
- Salience is carried as a per-extractor weight and beats recency for
  retention.
- Scoring is not understanding. Never collapse to label + score.

## The test of success

It is not benchmark accuracy on emotion words. It is whether a record
produced by one model from a person's conversation, read by another model
months later, preserves what mattered to that person, and shows its
evidence.

Benchmarks (GoEmotions) are validity checks, used once. The target corpora
are conversational and longitudinal.

## What the benchmark changed (2026-11)

sigbench full run 1 (2026-11-08 → 09; `sigbench/RESULTS-full1-2026-11-08.md`;
rulings R-bench-2026-11-09c) measured the test of success above on two real
corpora (the founder's archive, n = 1; REALTALK) with LoCoMo as a synthetic
comparator. What it changed:

- **The loss is at selection, not storage.** The whole transcript retains
  every item a later session returned to (retention 1.00). A long note
  written by the model (≈ 7,000 tokens) retains 0.89 of them and matches
  or beats the transcript on needed-later recall (0.69 against 0.67) at
  0.58 of its tokens. The short note retains 0.56, the per-session EDM
  record 0.44. Recall is lost where the writer chooses what to keep, not
  in how it is stored.
- **Significance-typed capture is not a recall advantage on conversation.**
  On REALTALK, with view, length and intent each controlled (a timestamped
  note, a long note, an intent-instructed note), the typed record gives no
  gain a plain note does not give at the same or fewer tokens; the
  per-session record is below the note (−0.18 recall, −0.14 forward
  questions), the sidecar matches the note at 3.4 × its tokens and its
  cues reach no prevalence, and the whole-window record loses most of what
  the per-session form kept. This is a result on daily chat. It is
  **untested on affect-dense substrates**: journal, memoir, companion text.
- **Intent moves H2 on n = 1.** One added sentence of intent in the note
  prompt raises retained-unvindicated significance recovery from 0.17 to
  0.30 (+0.12 [+0.05, +0.24]) on the one archive where H2 is measured, and
  passes the per-session record. The record's one dev advantage was an
  instruction effect. A dev reading, not a benchmark result.
- **Synthetic dialogue flatters structure.** On LoCoMo the per-session
  record nearly matches the note on recall and beats it on forward
  questions (0.86 against 0.79); on REALTALK it is far below on both.
  Model-authored sessions carry the fields a typed record asks for; people
  do not. Any claim about structured capture made on synthetic dialogue is
  suspect until it is made on real text.
- **EDM's live role is the measurement vocabulary**: the H2 definition
  (retained-unvindicated significance, `y` / `u` / `n`), the coding rubric
  and the evidence standard (located span, two-grader agreement, provenance).
  These are what sigbench runs on. **The record format is held as a
  hypothesis** for journal, memoir and companion text, where significance
  is dense and the writer's selection problem is different; it is not
  claimed for conversation.

The design principles above stand. The test of success stands, and it has
now been run.
