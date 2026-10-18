# Cues v1 — a catalogue of unsaid-signal patterns for text-only conversation

**Discovery note, 2026-10-18. Not normative. Vocabulary id for the schema sketch: `https://emotionaldatamodel.org/vocab/cues/v1` (proposed, unpublished).** Every example below is synthetic; no real person, no text from any corpus or archive.

## 0. How to read an entry

Each cue has a **code** (`rl:<slug>`), a **definition** stated as a departure from a norm (the norm is part of the definition: a cue is only a cue against it), a **lineage** where one exists in `literature.md` or an **EDM flag** where the pattern has no named source and is proposed here, one **synthetic example** with the cue span marked `⟦…⟧`, and the **labels it typically licenses**. A label is either **process** (something is being managed, avoided, returned to, held at a distance — read into `salience`, `motivation`, `context.scope`, the interpretive tier) or **content** (a felt quality, a harm, a trigger — read into `emotion.primary`, `narrative.harm`, `narrative.trigger`). Most cues license process only; where a cue can license content it is said, and the licence is always *typical*, never automatic. **Unit** says what the extractor must point at: a span (character offsets in one text), a pair of spans, a turn boundary, or a rate against a baseline (comparative; needs more than one text or a within-text baseline, and licenses nothing from one short text).

The catalogue is a hypothesis list for run 4 (`experiment-plan-run4.md`), where the questions are whether three extractors point at the same spans, agree on the cue, and license the same labels from the same cue. Nothing here is a field, a value or a profile.

## 1. Timing and turn shape (lineage: conversation analysis)

### `rl:delayed-reply` — delayed reply
**Definition.** A response that arrives later than the writer's own pace in the same exchange, where the delay is not accounted for in the text. Norm: the writer's median reply gap in the transcript. **Unit:** turn boundary with timestamps; without timestamps, not scorable (record `unscorable`).
**Lineage.** Jefferson 1989 (standard maximum silence); Pomerantz 1984 (delay as the first component of a dispreferred turn).
**Example.** `[21:04] A: do you want to come on Saturday?` / `⟦[23:51]⟧ B: yeah sure` (B's other replies in the thread came within two minutes).
**Licenses.** Process: reluctance, a dispreferred answer being managed; `motivation.action_tendency` (avoid / withdraw) as a *hypothesis*; `context.relationship` strain. Never content.

### `rl:going-quiet` — going quiet
**Definition.** A topic the writer raised, or was asked about, that receives no further turn from them while the exchange continues on other things. Norm: a raised topic is normally closed by its raiser. **Unit:** pair (the raising span, the point where the next turn should have been).
**Lineage.** Schegloff 1968 (conditional relevance: an absent second pair part is *noticeably* absent); Jefferson 1984 (exits from troubles-telling).
**Example.** `User: my brother called last night. ⟦Assistant: How did that go? User: anyway, can you help me draft the email to the landlord⟧`.
**Licenses.** Process: avoidance; `salience.recurrence` / `salience.tether` candidate (the quiet topic is often the tethered one); `narrative.subject` as a hypothesis *only if* the topic returns later (`rl:late-return`).

### `rl:preface` — the preface before the answer
**Definition.** A turn-initial token or clause that delays the substance of a response to a question ("well", "so", "ok so", "the thing is", "honestly"). Norm: the writer's other answers in the exchange begin with their substance. **Unit:** span.
**Lineage.** Pomerantz 1984; Schegloff & Lerner 2009 ("well"-prefaced responses).
**Example.** `Did you tell her? — ⟦Well, the thing is,⟧ she was already upset about the car.`
**Licenses.** Process: a dispreferred answer (refusal, disagreement, bad news) follows; `motivation.coping` (account-giving). Never content on its own.

### `rl:minimal-answer` — the minimal answer
**Definition.** A one-word or formulaic reply to a question that invited elaboration, in a text where the writer elaborates elsewhere. Norm: the writer's own answer length. **Unit:** span (the answer), comparative within the text.
**Lineage.** Grice 1975 (quantity flout); Pomerantz 1984.
**Example.** `How was the appointment? — ⟦Fine.⟧ Anyway. What did you want to ask about the trip?`
**Licenses.** Process: closure, withholding; `context.scope` (private); `salience.tether` candidate. Never content.

### `rl:late-return` — the late return
**Definition.** A topic that was closed, dropped or answered minimally earlier in the text comes back unprompted after other matters. Norm: closed topics stay closed. **Unit:** pair (the closing span, the returning span).
**Lineage.** Schegloff & Sacks 1973 (misplacement markers: "by the way", "oh, one more thing"); Jefferson 1984.
**Example.** `Fine. Anyway, the trip… [four turns on flights] ⟦Actually about the appointment — they want me back in six weeks.⟧`
**Licenses.** Process and, weakly, content: the returned topic is a strong candidate for `narrative.subject`, `narrative.trigger` and `salience.tether`; `salience.recurrence`.

## 2. Quantity (lineage: Grice; accounts)

### `rl:over-explaining` — over-explaining
**Definition.** Justification, reasons or background supplied for a statement that nobody questioned, beyond what the exchange needs. Norm: the writer's other statements stand unaccounted for. **Unit:** span (the account).
**Lineage.** Grice 1975 (quantity); Pomerantz 1984 (accounts as a component of dispreferred turns); Scott & Lyman 1968 (accounts).
**Example.** `I didn't go to the dinner. ⟦I had a lot on, and the trains were a mess that week, and honestly nobody would have noticed, it was a big table.⟧`
**Licenses.** Process: the statement is felt to need defending; `narrative.harm` *candidate* in the accounted-for act (what the account protects); `emotion.appraisal.attribution` is *not* licensed (the account is a management move, not a stated cause).

### `rl:unasked-denial` — the unasked-for denial
**Definition.** A negation of a state, motive or feeling that nothing in the text attributed to the writer ("not that I care", "I'm not upset", "it's not about the money"). Norm: denials answer attributions. **Unit:** span.
**Lineage.** Freud 1925 (*Die Verneinung*: the content of a repressed idea can enter consciousness on condition that it is negated); Labov 1972 (the negative as a comparator: what did not happen is evaluative).
**Example.** `She got the promotion. ⟦Not that I wanted it, I'm not even sure I'd have taken it.⟧ The new office is nice.`
**Licenses.** Content as a *hypothesis only*, attributable to the denied term (the denied feeling is the candidate `emotion.primary` / `narrative.harm`); the reading must carry the denial span and mark the licence as negated-content, never as stated.

### `rl:counting` — counting
**Definition.** Precise counts or dates offered where the exchange asked for none: the number of attempts, days since, times it happened, the exact date. Norm: approximation. **Unit:** span.
**Lineage.** None named for this form; **EDM flag `rl:counting` (proposed)**. Nearest: Labov 1972 (intensifiers; quantifiers as evaluation), Barthes 1968 (the precise, functionless detail; see `rl:precise-detail`).
**Example.** `We're fine. ⟦He's texted four times since the 12th, which is nineteen days.⟧`
**Licenses.** Process: the counted thing is being tracked, so it is salient; `salience.linkage_strength`, `emotion.intensity` (weight, not quality), `salience.tether` candidate; `narrative.subject` candidate (what is counted). Not `emotion.primary`.

### `rl:trailing-list` — the list that trails
**Definition.** An enumeration that does not close: "and… and…", items added after the sentence could have ended, or a list ending in "and stuff", "and everything", "etc." where the list matters. Norm: lists close. **Unit:** span.
**Lineage.** Jefferson 1990 (list construction; three-partedness and generalised list completers "and things like that"); Grice (quantity).
**Example.** `I packed up his room, the books, ⟦the chair, the jumper he wore all the time, the mug, and, and everything.⟧`
**Licenses.** Process: the list is where the weight is; `emotion.intensity` (weight); `salience.tether` (the listed objects as referents). Content only via the items themselves, which are stated.

### `rl:unfinished` — the unfinished sentence
**Definition.** A clause abandoned before its completion, marked by an ellipsis, a dash or a restart on a different sentence, where the completion is recoverable and the writer completes their sentences elsewhere. Norm: completion. **Unit:** span (the fragment).
**Lineage.** Local & Kelly 1986 (trail-off); Schegloff, Jefferson & Sacks 1977 (abandonment as a repair type); Freud 1901 (the dropped word).
**Example.** `I keep thinking if I'd just — ⟦well.⟧ It doesn't matter now.`
**Licenses.** Content as hypothesis: the recoverable completion is a candidate for `narrative.harm` or `narrative.meaning` (counterfactual); process: avoidance. The reading must give the fragment span, not the imagined completion, as evidence.

## 3. Manner (lineage: Grice; Ekman's process cues)

### `rl:hedge` — hedging
**Definition.** Epistemic or affective softeners on a claim the writer could make plainly ("I guess", "maybe", "sort of", "kind of", "I suppose", "a bit"), concentrated on one topic. Norm: the writer's plain statements elsewhere. **Unit:** span; comparative across topics within the text.
**Lineage.** Lakoff 1973 (hedges); Grice 1975 (manner); Prince, Frader & Bosk 1982 (shields vs approximators).
**Example.** `The job's good. My dad is ⟦sort of, I guess, kind of⟧ not speaking to me at the moment.`
**Licenses.** Process: the hedged topic is being managed; `salience.tether` and `narrative.subject` candidates; **not** `emotion.primary` (a hedge says nothing about what is felt).

### `rl:minimising` — minimising
**Definition.** Diminutives and downgraders on an event the text elsewhere treats as consequential ("just", "only", "a little", "it's nothing", "no big deal", "whatever"). Norm: the event's weight elsewhere in the text. **Unit:** span, with the contrasting span.
**Lineage.** Pomerantz 1984 (downgraded assessments); Labov 1972 (evaluation by contrast); Ekman 1985 (masking as a leakage condition).
**Example.** `It was ⟦just⟧ a comment, ⟦nothing really⟧. I didn't sleep. I keep replaying it.`
**Licenses.** Process: masking; the minimised event is a strong `narrative.trigger` / `narrative.harm` candidate; `emotion.intensity` read from the contrasting span, not from the minimiser.

### `rl:abstraction` — abstraction
**Definition.** A concrete event, person or act referred to by an abstract noun or a vague category ("the situation", "what happened", "the thing with my mother", "everything") in a text that is concrete elsewhere. Norm: the writer's concreteness. **Unit:** span.
**Lineage.** Grice 1975 (manner: obscurity); Pennebaker 2011 (noun / article profile of distance); Semin & Fiedler 1988 (linguistic category model: abstraction as distance).
**Example.** `Work's fine. Running's good. ⟦The situation at home⟧ is what it is.`
**Licenses.** Process: distance; the abstracted referent is a `narrative.subject` / `salience.tether` candidate; `context.scope` (private). Never content.

### `rl:agentless-passive` — the passive without an agent
**Definition.** An act with an agent the text knows is reported in the passive with the agent omitted ("the decision was made", "things were said"). Norm: the writer names agents elsewhere. **Unit:** span.
**Lineage.** Pennebaker 2011; Henley, Miller & Beazley 1995 (agentless passives in reports of violence); Grice (manner).
**Example.** `⟦Things were said⟧ at the funeral that can't be unsaid. Mum left early.`
**Licenses.** Process: responsibility or blame is being held off; `emotion.appraisal.attribution` is *not* licensed (the attribution is exactly what is withheld); `narrative.subject` candidate (the unnamed agent).

### `rl:register-shift` — register shift
**Definition.** A move into formal, clinical, legal or bureaucratic register on one topic in an otherwise informal text ("my spouse", "the deceased", "the incident", "proceedings"). Norm: the writer's register elsewhere. **Unit:** span.
**Lineage.** Goffman 1959 (front-region management); Labov 1972 (style shifting); Biber 1988 (register).
**Example.** `lol ok. anyway ⟦the individual concerned has been informed of the outcome⟧ and i'm going to bed`
**Licenses.** Process: distance, performance for an audience; `context.scope`; the shifted-on topic as `salience.tether` candidate.

### `rl:joke-at-weight` — the joke at the point of weight
**Definition.** Humour, self-mockery or a flippant aside inserted exactly where the text reaches its most consequential content. Norm: the writer's seriousness on the surrounding content. **Unit:** span, with the weighted span.
**Lineage.** Freud 1905 (jokes and the economy of psychic expenditure); Goffman 1959 (face-work; keying); Jefferson 1984 (laughter in troubles-telling).
**Example.** `They found something on the scan. ⟦Classic me, can't even get a boring result.⟧ They want to do another one.`
**Licenses.** Process: management of the weighted content; `motivation.coping` (humour as a stated coping *style* only if the text says so; otherwise a hypothesis); `emotion.intensity` from the weighted span.

### `rl:meta-comment` — the comment on the telling
**Definition.** A remark about the act of writing or saying it ("I don't know why I'm telling you this", "this sounds stupid", "sorry, long message"). Norm: telling without comment. **Unit:** span.
**Lineage.** Labov 1972 (external evaluation: the teller steps out of the narrative to evaluate it); Goffman 1959 (the performer commenting on the performance).
**Example.** `⟦I don't know why I'm writing this down.⟧ He's been dead three years.`
**Licenses.** Process: the told content is marked as significant by the teller; `salience.function` candidate (why the memory is being kept); `narrative.meaning` is *not* licensed by the meta-comment itself.

## 4. Repetition and return (lineage: Labov; EDM salience)

### `rl:repetition` — repetition
**Definition.** The same word, phrase or clause repeated within a short span beyond the needs of the sentence. Norm: single statement. **Unit:** span (all occurrences).
**Lineage.** Labov 1972 (repetition as an intensifier); Tannen 1989 (repetition in conversation).
**Example.** `It's fine. ⟦It's fine, it's fine.⟧ I just need the week to be over.`
**Licenses.** `emotion.intensity` (weight on the repeated content); process: self-persuasion when the repeated item is an assessment; the repeated referent as `salience.tether` candidate. Not `emotion.primary` from the repetition alone.

### `rl:recurring-subject` — the returning subject
**Definition.** A person, place, object or event that appears in several separate parts of a text, or across entries or sessions, without being the stated topic of any. Norm: a referent belongs to its topic. **Unit:** multiple spans; comparative across the text or corpus.
**Lineage.** **EDM flag `rl:recurring-subject` (proposed)**; nearest named: Labov (the point of a story is where the evaluation clusters); Conway & Pleydell-Pearce 2000 (self-defining memories recur). Maps to the v0.8.3 `recurrence_pattern` / v0.9 `salience.recurrence`.
**Example.** `[entry 1] …passed the old flat on the way… [entry 3] …the café near ⟦the old flat⟧… [entry 7] …dreamt I was back in ⟦the flat⟧ again…`
**Licenses.** `salience.recurrence`, `salience.tether` (referent), `narrative.subject` candidate; `salience.linkage_strength`. Content no.

### `rl:rereading` — rereading one's own words
**Definition.** The writer quotes, paraphrases or refers back to something they wrote earlier in the same text or an earlier entry ("I said last week that…", "reading this back…"). Norm: forward telling. **Unit:** pair (the original span if present, the rereading span).
**Lineage.** **EDM flag `rl:rereading` (proposed)**; nearest: Labov (external evaluation), Pennebaker & Beall 1986 (expressive writing revisits).
**Example.** `⟦I wrote "it's over" on Tuesday. Reading it back it looks like someone else's handwriting.⟧`
**Licenses.** `narrative.integration` candidate (the experience being re-fitted), `emotion.temporal_profile` (the shift between then and now), `narrative.meaning` only if the rereading states a conclusion (then it is stated, not a cue).

### `rl:self-repair` — the self-repair
**Definition.** A word or phrase replaced by the writer within the same turn ("angry — well, upset", "my ex, I mean Sam"), with the first version left visible. Norm: the final form only. **Unit:** pair (replaced, replacement).
**Lineage.** Schegloff, Jefferson & Sacks 1977 (self-initiated self-repair); Freud 1901 (substitution: the first form as the competing intention).
**Example.** `I was ⟦furious — no, disappointed,⟧ when he didn't show.`
**Licenses.** Content as a *pair*: the replaced word is a candidate `emotion.primary` / `narrative.harm` with the replacement as the stated value; the reading must carry both spans and record which was final. The replacement is what the stated-only reading takes; the cue licenses the replaced word only as a hypothesis.

## 5. Person, tense and distance (lineage: Pennebaker; Freud)

### `rl:tense-shift-person` — tense shift about a person
**Definition.** A person referred to in a tense that does not match their status as the text otherwise gives it: the present for someone the text says is dead or gone ("Mum hates that song"), the past for someone present ("he was a good husband" of a living spouse), or a switch between the two within the text. Norm: tense consistent with the stated status. **Unit:** span, with the status span.
**Lineage.** Pennebaker 2011 (verb tense and psychological distance); Freud 1901 (the slip); Klass, Silverman & Nickman 1996 (continuing bonds; the present-tense dead).
**Example.** `Dad died in March. ⟦He's always on at me⟧ about the car. I should sort the car.`
**Licenses.** Content hypothesis: `narrative.harm` (the loss), `salience.tether` (the person; `tether.type` person), `emotion.temporal_profile` (unresolved / ongoing); `emotion.primary` not from the tense alone (grief is the obvious over-reading; the text may say something else).

### `rl:pronoun-distance` — pronoun distancing
**Definition.** The writer refers to their own experience in the second person or the generic ("you just get on with it", "one copes") on one topic while using "I" elsewhere. Norm: the writer's "I" rate. **Unit:** span; comparative within the text.
**Lineage.** Pennebaker 2011; Orvell, Kross & Gelman 2017 (generic "you" as distancing from negative experience).
**Example.** `I love the new place. ⟦You don't really expect your mother to stop calling, you just notice one day that she hasn't.⟧`
**Licenses.** Process: distance from the "you"-told content; that content as `narrative.harm` / `narrative.subject` candidate; `context.scope`. Not content directly.

### `rl:dropped-name` — the dropped name
**Definition.** A person named earlier becomes a pronoun, a role or a description ("him", "my ex", "that man", "the person I mentioned") without a change of reference, or is never named where the text names others. Norm: the writer's naming practice. **Unit:** pair (the named span if any, the unnamed span).
**Lineage.** **EDM flag `rl:dropped-name` (proposed)**; nearest: Pennebaker 2011 (pronouns and distance); Schegloff 1996 (reference to persons).
**Example.** `Sam and Jo came. ⟦He⟧ brought the dog. ⟦He⟧ stayed about an hour. Jo and I did the dishes.` (the third guest is never named).
**Licenses.** Process: distance from the unnamed person; `narrative.subject` and `salience.tether` candidates; `context.relationship` (strained) as a hypothesis. Not content.

### `rl:slip` — the slip
**Definition.** A wrong name, wrong word, wrong number or wrong pronoun that the surrounding text makes identifiable as wrong and that is not a typographical error (the substituted form is a real, related word). Norm: the correct form the text itself establishes. **Unit:** span.
**Lineage.** Freud 1901 (parapraxis).
**Example.** `I told Dan — ⟦I told Mark⟧ — that I'd think about it.` (Dan is the ex-partner named earlier; Mark is the current one; the text does not correct itself).
**Licenses.** Hypothesis only: the substituted referent as a candidate `narrative.subject` / `salience.tether`. Flag `typo_risk` on every slip reading; a single slip licenses nothing without a second cue on the same referent.

### `rl:we-shift` — "we" appearing or disappearing
**Definition.** A change in the writer's use of "we" / "us" for a relationship the text otherwise treats as stable: "we" replaced by "I and he", or "we" appearing for a person previously held at a distance. Norm: the writer's pronoun regime for that relationship. **Unit:** pair; comparative within the text.
**Lineage.** Pennebaker 2011 ("we" and closeness); Simmons, Gordon & Chambless 2005 (we-talk in couples).
**Example.** `⟦We⟧ always did the market on Sundays. ⟦I⟧ went this week, and ⟦he⟧ did whatever he does.`
**Licenses.** `context.relationship` (change), `narrative.valence_shift` candidate, `salience.tether` (person); process: distance. Not content.

## 6. Relation and topic (lineage: Grice; conversation analysis)

### `rl:topic-change` — abrupt topic change
**Definition.** A move to an unrelated topic without a transition marker at a point where the prior topic was open, in a text whose other transitions are marked. Norm: marked transitions. **Unit:** turn or sentence boundary (pair of spans).
**Lineage.** Grice 1975 (relation flout); Jefferson 1984 (stepwise vs abrupt exits from troubles-telling); Sacks 1992 (topic shift).
**Example.** `…and then she said she'd rather I didn't come to the christening. ⟦Did you see the match?⟧`
**Licenses.** Process: exit from the open topic; the abandoned topic as `narrative.trigger` / `salience.tether` candidate; `motivation.action_tendency` (avoid) hypothesis. Not content.

### `rl:deflection` — the question answered with a question
**Definition.** A direct question about the writer's state or an event answered by a question, a redirection to the asker, or a general statement. Norm: an answer. **Unit:** pair (question, non-answer).
**Lineage.** Schegloff 2007 (counters); Clayman 2001 (answers and evasions); Grice (relation).
**Example.** `Assistant: Are you okay with how it ended? User: ⟦Is anyone ever? How do people usually handle this?⟧`
**Licenses.** Process: avoidance; `context.scope`; `motivation.need` as a hypothesis (what the redirect asks for). Not content.

### `rl:precise-detail` — the precise, functionless detail
**Definition.** A detail given with unusual precision (colour, brand, time to the minute, what someone was wearing) that plays no role in the event told. Norm: details that serve the telling. **Unit:** span.
**Lineage.** Freud 1899 (screen memories: the vivid, indifferent detail); Barthes 1968 (*l'effet de réel*); Labov & Waletzky 1967 (orientation).
**Example.** `He told me on the stairs. ⟦The carpet was that green with the orange fleck, and the radio was on in the kitchen, the one with the broken aerial.⟧ Then he left.`
**Licenses.** `salience.retrieval_cues` (the detail is exactly what the v0.8.3 `recall_triggers` field asked for), `salience.linkage_strength`, `emotion.intensity` (weight); the surrounding event as `narrative.trigger`. Not content.

### `rl:absent-party` — the absent party
**Definition.** A person who should figure in the event as told (a parent at a wedding, a partner in a move) is not mentioned, or is mentioned once and then dropped from a scene they were in. Norm: participants are mentioned. **Unit:** span (the scene) with a null second span; comparative.
**Lineage.** Schegloff 1968 (noticeable absence); Grice (quantity); **EDM flag for the written form (proposed)**.
**Example.** `⟦Moving day. Mum did the kitchen, my sister drove the van, the neighbours helped with the sofa.⟧` (the text's earlier entries have a partner in the household).
**Licenses.** `narrative.subject` and `salience.tether` candidates for the absent person; `context.relationship` hypothesis. Never content; the reading must state the expectation it relies on (which earlier span makes the absence noticeable).

## 7. Evaluation (lineage: Labov)

### `rl:counterfactual` — the counterfactual
**Definition.** A statement of what did not happen, could have happened or would have happened ("if I'd gone", "she could have called", "it should have been me"). Norm: the actual. **Unit:** span.
**Lineage.** Labov 1972 (comparators: negatives, futures, modals as evaluation); Kahneman & Miller 1986 (norm theory).
**Example.** `We got the diagnosis on the Friday. ⟦If I'd pushed for the scan in January it would have been caught.⟧`
**Licenses.** Content: `narrative.harm` candidate (what the counterfactual protects or regrets), `narrative.meaning` candidate (the conclusion the counterfactual implies), `motivation.risk_posture`, `emotion.appraisal.attribution` (self / other) *when the counterfactual names the agent*; `emotion.primary` not from the device alone (regret, guilt and relief all use it).

### `rl:intensifier-stack` — the intensifier stack
**Definition.** Two or more intensifiers on one assessment ("really really", "so so tired", "absolutely completely done"), or a superlative with no comparison class ("the worst", "the best day"). Norm: single intensification. **Unit:** span.
**Lineage.** Labov 1972 (intensifiers; external evaluation); Pomerantz 1984 (extreme case formulations).
**Example.** `I'm ⟦so, so tired⟧ of being the one who remembers everything.`
**Licenses.** `emotion.intensity` (weight), `salience.linkage_strength`; the intensified assessment is stated content (not a cue) and is read as such.

### `rl:open-coda` — the coda that does not close
**Definition.** A narrative or entry that ends on a formulaic closer that does not resolve it ("anyway.", "so that's that.", "we'll see.", "it is what it is."). Norm: a coda that returns the teller to the present (Labov). **Unit:** span (the closer).
**Lineage.** Labov & Waletzky 1967 (the coda); Jefferson 1984 (closing troubles-telling).
**Example.** `The letter came. I haven't opened it. ⟦Anyway.⟧`
**Licenses.** `narrative.integration` (unintegrated; the null-driven field's clearest cue), `emotion.temporal_profile` (ongoing / unresolved), `salience.trajectory` hypothesis. Not content.

### `rl:unprompted-contrast` — the unprompted contrast
**Definition.** "But" or "though" introducing a qualification that nothing in the text called for, typically after a positive statement ("it was a lovely day, but", "I'm happy for her, though"). Norm: unqualified statements. **Unit:** span (the qualification).
**Lineage.** Labov 1972 (correlatives and comparators); Pomerantz 1984 (second assessments); Grice (relation).
**Example.** `The wedding was perfect. ⟦But I kept looking at the door.⟧`
**Licenses.** `narrative.valence_shift`, `emotion.secondary` candidate (stated if the qualification names a feeling), `narrative.subject` candidate (what the qualification is about); content only via what the qualification states.

### `rl:explicative-overload` — the explicative overload
**Definition.** Causal connectives ("because", "since", "so that", "which is why") stacked on one event beyond what a single reason needs. Norm: one reason. **Unit:** span.
**Lineage.** Labov 1972 (explicatives as evaluation); Pennebaker, Mayne & Francis 1997 (causal words in expressive writing).
**Example.** `I left early ⟦because the room was hot and because I had an early start and because, honestly, since the move I can't do crowds, which is why I said I'd drive.⟧`
**Licenses.** Process: the event is being made sense of (cf. `rl:over-explaining`, which protects; this constructs); `narrative.integration` candidate (sense-making in progress), `narrative.meaning` candidate if a conclusion is stated among the reasons. Not `emotion.appraisal.attribution` unless a reason names an agent.

## 8. Summary table

| Code | Family | Unit | Lineage / flag | Typical licence |
|---|---|---|---|---|
| `rl:delayed-reply` | timing | turn + timestamp | Jefferson; Pomerantz | process |
| `rl:going-quiet` | timing | pair | Schegloff; Jefferson | process; tether / subject candidate |
| `rl:preface` | timing | span | Pomerantz | process |
| `rl:minimal-answer` | timing | span, comparative | Grice; Pomerantz | process |
| `rl:late-return` | timing | pair | Schegloff & Sacks | subject / trigger / tether candidate |
| `rl:over-explaining` | quantity | span | Grice; Pomerantz | process; harm candidate |
| `rl:unasked-denial` | quantity | span | Freud 1925; Labov | negated-content hypothesis |
| `rl:counting` | quantity | span | **EDM flag** | weight; tether / subject |
| `rl:trailing-list` | quantity | span | Jefferson 1990 | weight; tether |
| `rl:unfinished` | quantity | span | Local & Kelly; SJS 1977 | harm / meaning hypothesis |
| `rl:hedge` | manner | span, comparative | Lakoff; Grice | process |
| `rl:minimising` | manner | span + contrast | Pomerantz; Ekman | trigger / harm candidate; intensity from contrast |
| `rl:abstraction` | manner | span | Grice; Pennebaker; Semin & Fiedler | process; subject / tether |
| `rl:agentless-passive` | manner | span | Pennebaker; Henley et al. | process; subject |
| `rl:register-shift` | manner | span | Goffman; Labov | process; scope |
| `rl:joke-at-weight` | manner | span + weight | Freud 1905; Goffman; Jefferson | process; coping hypothesis |
| `rl:meta-comment` | manner | span | Labov; Goffman | salience.function candidate |
| `rl:repetition` | repetition | span | Labov; Tannen | intensity; tether |
| `rl:recurring-subject` | repetition | multi-span, comparative | **EDM flag** | recurrence; tether; subject |
| `rl:rereading` | repetition | pair | **EDM flag** | integration; temporal_profile |
| `rl:self-repair` | repetition | pair | SJS 1977; Freud | content pair (replaced / final) |
| `rl:tense-shift-person` | person | span + status | Pennebaker; Klass et al. | harm / tether / temporal_profile hypothesis |
| `rl:pronoun-distance` | person | span, comparative | Pennebaker; Orvell et al. | process; harm / subject candidate |
| `rl:dropped-name` | person | pair | **EDM flag** | process; subject / tether |
| `rl:slip` | person | span | Freud 1901 | hypothesis only; `typo_risk` |
| `rl:we-shift` | person | pair, comparative | Pennebaker; Simmons et al. | relationship; valence_shift |
| `rl:topic-change` | relation | boundary | Grice; Jefferson | process; trigger / tether |
| `rl:deflection` | relation | pair | Schegloff; Clayman | process; need hypothesis |
| `rl:precise-detail` | relation | span | Freud 1899; Barthes; Labov | retrieval_cues; linkage; weight |
| `rl:absent-party` | relation | span + null, comparative | Schegloff; **EDM flag** | subject / tether candidate |
| `rl:counterfactual` | evaluation | span | Labov; Kahneman & Miller | harm / meaning / attribution candidate |
| `rl:intensifier-stack` | evaluation | span | Labov; Pomerantz | intensity; linkage |
| `rl:open-coda` | evaluation | span | Labov; Jefferson | integration; temporal_profile |
| `rl:unprompted-contrast` | evaluation | span | Labov; Pomerantz | valence_shift; secondary |
| `rl:explicative-overload` | evaluation | span | Labov; Pennebaker et al. 1997 | integration; meaning candidate |

35 cues; 6 carry an EDM flag (no named lineage for the written form), 29 have a named lineage. Nine are comparative (need a within-text or cross-text baseline) and one (`rl:delayed-reply`) needs timestamps; run 4 scores those as `unscorable` where the baseline or timestamp is absent rather than letting an extractor guess.

## 9. Rules the catalogue imposes on any reading

1. **A cue is a span plus a norm.** No cue is recorded without the span it rests on and the catalogue code that names the norm it departs from.
2. **Process is not content.** A cue in the process column licenses a reading into `salience`, `motivation`, `context.scope`, `context.relationship` or the interpretive tier; it never populates `emotion.primary`, `narrative.harm` or `narrative.trigger` on its own. Those fields keep their stated or interpreted basis; a cue may *point at* the span the field should be read from (a candidate), and that pointing is what the `reading` block records.
3. **One cue licenses a hypothesis; two cues on the same referent license a candidate.** The catalogue's "candidate" readings become field values only through the ordinary field rule (interpretation attributable to a passage); the reading layer's job is to make the passage findable and the licence inspectable.
4. **Flags travel with the reading.** `typo_risk` (slip), `unscorable` (no timestamp / no baseline), `negated` (unasked denial), `model_authored_risk` (companion-arm text where the span may be model-written).
5. **Nothing trait-shaped.** No cue licenses a trait, a diagnosis or a stable disposition; the `trait` domain stays opt-in and unextracted.

## 10. Additional sources named in this catalogue (beyond `literature.md` §10)

Barthes 1968 (*L'effet de réel*); Biber 1988 (*Variation across Speech and Writing*); Clayman 2001 (answers and evasions, *Language in Society*); Conway & Pleydell-Pearce 2000 (self-memory system, *Psychological Review*); Freud 1899 (screen memories), 1905 (jokes), 1925 (negation); Henley, Miller & Beazley 1995 (*Journal of Language and Social Psychology*); Jefferson 1984 (troubles-telling), 1990 (list construction); Kahneman & Miller 1986 (norm theory, *Psychological Review*); Klass, Silverman & Nickman 1996 (*Continuing Bonds*); Lakoff 1973 (hedges, *Journal of Philosophical Logic*); Local & Kelly 1986 (*Human Studies*); Orvell, Kross & Gelman 2017 (*Science*); Pennebaker & Beall 1986 (*Journal of Abnormal Psychology*); Pennebaker, Mayne & Francis 1997 (*JPSP*); Pomerantz 1984; Prince, Frader & Bosk 1982; Sacks 1992 (*Lectures on Conversation*); Schegloff 1968 (*American Anthropologist*), 1996, 2007 (*Sequence Organization*); Schegloff & Lerner 2009; Schegloff & Sacks 1973 (*Semiotica*); Schegloff, Jefferson & Sacks 1977 (*Language*); Scott & Lyman 1968 (*American Sociological Review*); Semin & Fiedler 1988 (*JPSP*); Simmons, Gordon & Chambless 2005 (*Psychological Science*); Tannen 1989 (*Talking Voices*). Cited from memory of the works; verify before any normative use.
