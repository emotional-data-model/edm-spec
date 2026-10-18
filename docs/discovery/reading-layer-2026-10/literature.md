# The sign lineage: what the unsaid has been read from, and what each reading lacks for text-only conversation

**Discovery note, 2026-10-18. Not normative. No API calls.** Companion to `cues-v1.md` (the cue catalogue), `schema-sketch.md` (the additive `evidence` / `reading` blocks) and `experiment-plan-run4.md` (the pre-registered span and cue experiment, not frozen, not run).

## 0. Why a lineage

Runs 1–3 established which EDM fields different extractors fill the same way from the same text. What they did not touch is *where in the text* a value comes from, and whether an extractor's value rests on what the text says or on what the text does: the pause before an answer, the subject that keeps coming back, the sentence that explains more than it was asked. EDM's rule is interpretation only, attributed — every value attributable to a passage. For most of the comparable tier that passage is a statement. For the interpretive tier (`subject`, `trigger`, `drive`, `tether`, `temporal_profile`, `memory_type`, `linkage_strength`, `risk_posture`) and for several stated-only fields the passage is often not a statement at all but a *sign*: something given off rather than given.

The reading of signs has a long record. Eight bodies of work, from Darwin to Pennebaker, each proposed a class of involuntary or semi-voluntary signal and a method for reading it. None was built for the situation EDM now faces: a text-only transcript, often one side of a conversation with a machine, read by a language model that is itself a strong producer of the same signs. The table below says, for each, what it contributes to a reading layer and what it lacks here. Sources are cited by the work, not fetched for this note; the reader checks them.

## 1. Darwin 1872 — *The Expression of the Emotions in Man and Animals*

**Claim.** Expressions are the residue of serviceable habits: movements that once served a purpose persist as involuntary signs of the state that produced them (the principle of serviceable associated habits, antithesis, direct nervous action). The sign is *not addressed to anyone*; it is a leak from the body, and its readability is a by-product.

**Contributes.** The founding distinction between an expression that *is* the state and a report *about* the state. For a reading layer: the licence to treat an involuntary textual feature (a repetition, a tense slip) as evidence of a state the writer did not announce, on the same footing Darwin gave to blushing.

**Lacks for text.** Darwin's signs are bodily and continuous; text has no face. Every textual sign passes through a motor act (typing) that is slower and more editable than a flinch, so the involuntary / voluntary line is blurred: a delayed reply may be a sign or a meeting. There is no antithesis principle for prose. And Darwin's reader is a naturalist watching a body; the reader here is a model that was trained on the signs it reads and tends to see them where they are not (run 1's null-precision failures on `meaning` are the near case).

## 2. Freud 1901 — *The Psychopathology of Everyday Life* (parapraxis)

**Claim.** Slips of the tongue and pen, forgettings, misreadings and bungled actions are not noise: they are determined, and what determines them is a competing intention the speaker has set aside. The sign is *the error itself*, and reading it means asking what the correct form would have been and what the deviation substitutes for.

**Contributes.** Three things a reading layer needs: (1) the method of the *counterfactual norm* — a sign is a departure from what the writer would otherwise have written, so the reading must state the norm it departs from; (2) *substitution* as a cue class (the wrong name, the wrong tense, the wrong pronoun); (3) the warning that the reader supplies the interpretation and should hold it as a hypothesis attributable to the slip, not as a fact about the writer.

**Lacks for text.** Typos and autocorrect make the slip channel noisy in a way Freud's dictated clinic was not; a text-only reader cannot distinguish a keyboard error from a substitution. The method also assumes a reader who can ask the writer what they meant, and a theory of the unconscious that EDM must not import (interpretation only, no inferred traits or hidden motives — the EU AI Act boundary the schema is built on). The usable residue is the form, not the theory: *this is where the writing departed from its own norm*.

## 3. Goffman 1959 — *The Presentation of Self in Everyday Life* (expressions given and given off)

**Claim.** In interaction a person *gives* expressions (what they say, intending it to be taken as communication) and *gives off* expressions (what they do that others read as symptomatic, which the person may not control and may not intend). Audiences attend to the given-off because it is harder to fake; performers learn to manage it; the result is an information game.

**Contributes.** The cleanest vocabulary for the layer: EDM's stated-only and comparable fields read what is *given*; the reading layer reads what is *given off*. Goffman also supplies the *audience* as a variable — a sign is given off *to someone*, and a journal, a companion transcript and a dialogue have different audiences and therefore different management. His front / back region distinction maps onto `context.scope` and the conversational arms' difference in run 1.

**Lacks for text.** Goffman's given-off channel is overwhelmingly non-verbal: posture, glance, tone. In text the given-off channel is thin and mostly temporal or structural (timing, length, order, repetition, what is skipped). The audience of a machine transcript is also unusual: the writer may perform for the model, for a future self, or for no one, and the model cannot tell which. Goffman offers no measurement; his categories are read by a competent member, not scored.

## 4. Ekman & Friesen 1969; Ekman 1985 — leakage and deception clues

**Claim.** When a felt state is masked, the mask is imperfect: the state *leaks* through channels under less control (the body more than the face, the face more than words; micro-expressions; timing asymmetries). Leakage clues reveal *that* something is masked and sometimes *what*; deception clues reveal only that a performance is being managed.

**Contributes.** The distinction between a cue that licenses a *content* label (what is felt) and a cue that licenses only a *process* label (that something is being managed). That distinction is the backbone of `cues-v1.md`: most textual cues (hedging, over-explaining, minimising) are process cues and license a reading of *management*, not of the masked state. Ekman's channel hierarchy also suggests a textual analogue: the content of a sentence is more controlled than its length, order and timing.

**Lacks for text.** The empirical base is faces and bodies, and the strong claims (micro-expressions, universality) are contested even there; nothing in it was validated on prose. Text has no low-control channel of comparable bandwidth, and what it has (typing speed, edit history, reply latency) is usually not in the transcript. Ekman's framing is adversarial (lie detection), which is the wrong stance for a journal; the reading layer needs the leak without the suspicion.

## 5. Grice 1975 — conversational implicature

**Claim.** Speakers mean more than they say, and hearers recover it by assuming cooperation (the maxims of quantity, quality, relation, manner) and asking what the speaker must believe for their utterance to be cooperative. A *flout* — saying too little, too much, the irrelevant, the obscure — is the sign; the implicature is what the flout licenses.

**Contributes.** The only entry in the lineage that is already a theory of *text* and already a theory of *licence*: an implicature is a reading the utterance licenses under stated assumptions, defeasible, attributable to a specific flout. This is the model for the `reading` block's `label_licensed`. Quantity flouts (over-explaining, the one-word answer), relation flouts (the abrupt topic change) and manner flouts (hedging, the passive, the abstract noun) are each a cue class with a named lineage.

**Lacks for text-with-a-model.** Grice assumes two cooperative humans who share a context. In a companion transcript one party is a model that is maximally cooperative by construction and the other may not be addressing it at all; in a journal there is no hearer. The maxims also presuppose a norm of relevance that a model infers from training, so a model reading implicature tends to over-recover (it finds relevance everywhere). Grice gives no account of silence or delay, which text-only conversation makes central.

## 6. Sacks, Schegloff & Jefferson 1974; Jefferson 1989 — silence, delay and preference in turn-taking

**Claim.** Conversation is organised turn by turn; gaps, pauses and delays are *meaningful* against a standard maximum silence (Jefferson's ~1 second) and against the preference structure of adjacency pairs: a dispreferred response (refusal, disagreement, bad news) is characteristically *delayed*, *prefaced* ("well…"), *mitigated* and *accounted for*. The sign is the shape of the turn, and it is read by the participants in real time.

**Contributes.** A worked theory of *delay as a sign* and of the dispreferred-turn shape (delay + preface + hedge + account), which is directly observable in chat transcripts with timestamps and in dialogue transcripts with turn boundaries. It also licenses reading *the absence of a response* as a response. For the catalogue: delayed reply, going quiet, the preface, the account, the minimal answer.

**Lacks for text.** Timestamps are often absent or unreliable, and a text gap has no standard maximum: a two-hour reply gap in a messaging app is unremarkable. Turn shape in text is editable (the preface can be deleted before sending). Conversation analysis refuses to attribute inner states at all — it reads the interactional job a turn does, not what the speaker feels — so the licence it gives is for *process* labels and for `context.scope` / relational readings, never for `emotion.primary`.

## 7. Labov & Waletzky 1967; Labov 1972 — evaluation devices in narrative

**Claim.** A personal narrative has a structure (abstract, orientation, complicating action, evaluation, result, coda), and *evaluation* — the teller's means of indicating the point of the story, why it is worth telling — is carried by devices that are partly external (the teller says "it was the worst day") and partly embedded: intensifiers, repetition, comparators (negatives, futures, modals: what did *not* happen, what *could* have), correlatives, explicatives. The embedded devices are the sign: the point of the story leaks through its grammar.

**Contributes.** The strongest fit in the lineage to EDM's narrative domain. Evaluation devices are *textual*, *countable* and *validated on elicited narratives*, and they map to fields: external evaluation to `meaning` and `summary`; comparators (the negative, the modal, the counterfactual) to `harm`, `drive`, `risk_posture`; repetition and intensifiers to `intensity` and `salience`; the coda to `integration` and `temporal_profile`. Labov also gives the layer its best test: the point of a story is what its evaluation devices cluster around, which is a span, not a sentence.

**Lacks for text-with-a-model.** The devices were catalogued on oral narratives of personal experience elicited by an interviewer; journals, companion transcripts and diaries do not reliably have the structure, and conversational turns often lack a complicating action at all. The embedded devices are also exactly what language models produce fluently, so a model-written or model-coached text (the companion arm) carries evaluation devices that are not the subject's. There is no account of what the teller leaves out.

## 8. Pennebaker 2011 — function words (*The Secret Life of Pronouns*; LIWC)

**Claim.** The small, closed-class words — pronouns, articles, prepositions, auxiliaries — are produced with little attention and carry stable signal about the writer's attention, status and state: first-person singular with depression and self-focus, pronoun shifts with changes in attention, "we" with closeness, the absence of "I" with distance or status. The sign is a *rate*, read across a text or a corpus, not a passage.

**Contributes.** The only entry with a quantitative, text-native, replicated base, and the one that supplies the *distance* family of cues: the shift from "I" to "you" or "one" when a subject gets close, the drop of the agent in a passive, the pronoun that replaces a name. It also fixes the unit: these signs are distributional and need a baseline (the writer's own rate elsewhere in the text or corpus), which is why the catalogue marks them *comparative*.

**Lacks for text-with-a-model.** The effects are small and population-level; a single text rarely licenses a label from its pronoun rate, and a model reading one text will over-read. LIWC rates were validated on human writing, and model-produced or model-coached text has its own function-word profile. Pennebaker's signal is a state-trait mix, and EDM's trait domain is opt-in and excluded from extraction; the layer may use function words only for *within-text shifts* (a span where the pronoun regime changes), never for a trait reading.

## 9. What the lineage adds up to

| Source | Sign class | Licenses | Unit | Validated on | Missing for EDM |
|---|---|---|---|---|---|
| Darwin | involuntary expression | content (the state) | body, continuous | observation | no textual channel; reader bias |
| Freud | the slip, the substitution | hypothesis (competing content) | the error | clinic | typo noise; theory EDM must not import |
| Goffman | given off vs given | process (management), audience | the performance | fieldwork | thin textual given-off channel; no measure |
| Ekman | leakage, timing asymmetry | process; sometimes content | face, timing | lab (contested) | adversarial stance; no prose base |
| Grice | the flout | defeasible content, attributable | the utterance | philosophy of language | two cooperative humans; no silence |
| Sacks / Schegloff / Jefferson | delay, preference shape | process, relational | the turn | recorded talk | timestamps; refuses inner states |
| Labov | evaluation devices | the point; intensity; counterfactuals | the clause / span | elicited oral narrative | model-fluent devices; omission |
| Pennebaker | function-word rates | attention, distance, closeness | the rate vs a baseline | corpora | single-text over-reading; trait mix |

Three things follow for the reading layer.

1. **Every cue needs a stated norm.** Freud's counterfactual, Grice's maxim, Jefferson's standard gap, Pennebaker's baseline: a sign is a departure, and the reading must say from what. The `reading` block therefore carries the cue code (which names the norm in the catalogue) and the span (where the departure is), never the label alone.
2. **Most textual cues license process, not content.** Hedging, over-explaining, minimising, delay and topic change say that something is being managed; they do not say what is felt. The catalogue marks each cue with the labels it *typically* licenses and keeps the process / content distinction; an extractor that reads `emotion.primary` from a hedge is over-reading, and run 4's cue → label stability measure is designed to catch it.
3. **The model is a sign-producer reading signs.** Every entry in the lineage assumes a reader who did not write the signs. A language model has read millions of hedges and slips and will find them; the companion arm's texts were partly produced by one. The experiment therefore scores span agreement (did three models point at the same place?) before label agreement, and the private arm (the founder's own archive, deferred) is the only arm whose texts no model touched.

## 10. Sources (cited, not fetched for this note)

- Darwin, C. (1872). *The Expression of the Emotions in Man and Animals.* John Murray.
- Freud, S. (1901). *Zur Psychopathologie des Alltagslebens* (*The Psychopathology of Everyday Life*).
- Goffman, E. (1959). *The Presentation of Self in Everyday Life.* Doubleday Anchor.
- Ekman, P. & Friesen, W. V. (1969). Nonverbal leakage and clues to deception. *Psychiatry*, 32(1), 88–106. Ekman, P. (1985). *Telling Lies.* Norton.
- Grice, H. P. (1975). Logic and conversation. In Cole & Morgan (eds), *Syntax and Semantics 3: Speech Acts*, 41–58. Academic Press.
- Sacks, H., Schegloff, E. A. & Jefferson, G. (1974). A simplest systematics for the organization of turn-taking for conversation. *Language*, 50(4), 696–735. Jefferson, G. (1989). Preliminary notes on a possible metric which provides for a "standard maximum" silence of approximately one second in conversation. In Roger & Bull (eds), *Conversation*, 166–196. Pomerantz, A. (1984). Agreeing and disagreeing with assessments (dispreferred turn shape). In Atkinson & Heritage (eds), *Structures of Social Action*.
- Labov, W. & Waletzky, J. (1967). Narrative analysis: oral versions of personal experience. In Helm (ed), *Essays on the Verbal and Visual Arts*, 12–44. Labov, W. (1972). The transformation of experience in narrative syntax. In *Language in the Inner City*, 354–396. University of Pennsylvania Press.
- Pennebaker, J. W. (2011). *The Secret Life of Pronouns.* Bloomsbury. Tausczik, Y. R. & Pennebaker, J. W. (2010). The psychological meaning of words: LIWC and computerized text analysis methods. *Journal of Language and Social Psychology*, 29(1), 24–54.
