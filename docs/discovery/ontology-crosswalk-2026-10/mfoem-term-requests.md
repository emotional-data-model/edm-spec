# MFOEM new-term requests — draft text

Discovery output, 2026-10-17. Not yet filed. Target: the Emotion Ontology (MFOEM) issue tracker, `jannahastings/emotion-ontology` on GitHub, which the OBO PURL `http://purl.obolibrary.org/obo/mfoem.owl` resolves to (version checked: 2025-07-31; `mfoem_classes.json`). Seven EDM `emotion_primary` values have no MFOEM class: awe (EDM `wonder` / `reverence`), gratitude, relief, nostalgia (EDM `longing`), tenderness, frustration, and wonder itself. Each request below follows the OBO new-term convention (label, parent, textual definition with source, synonyms, rationale, example of use). Definitions are drafted from the fetched frameworks in `frameworks.json`; where a definition leans on a source not in the reference set it is marked [KNOWLEDGE] so the filer can replace it.

Common preamble for every issue:

> Requested on behalf of the Emotional Data Model (EDM, MIT, emotionaldatamodel.org), an open artifact format that records explicitly stated emotional content. EDM codes its emotion field to MFOEM emotion-process subclasses (version 2025-07-31). The term below is a canonical EDM value with no MFOEM home; at present it is coded `relation: related` to the nearest class, which loses the distinction the subject made.

---

## 1. awe

- **Label:** awe
- **Parent:** emotion process (MFOEM:000001); also assert positive valence (MFOEM:000211 positive emotion) as the default profile, noting that threat-flavoured awe exists.
- **Definition:** An emotion process elicited by the appraisal of something as vast, beyond one's current frame of reference, and requiring accommodation of existing mental structures; characterised by a sense of smallness of the self and heightened attention.
- **Definition source:** Keltner, D. & Haidt, J. (2003). Approaching awe, a moral, spiritual, and aesthetic emotion. *Cognition and Emotion* 17(2), 297–314 [KNOWLEDGE: not fetched]. Listed as a category by Cowen & Keltner (2017, PNAS, fetched) and in the Hume expression-measurement taxonomy (fetched); Plutchik's primary dyad fear + surprise (knowledge-reconstructed, see `frameworks.json#plutchik`).
- **Synonyms:** wonder (broad), reverence (narrow, directed at a person or sacred object).
- **Why MFOEM needs it:** Awe is the only Cowen & Keltner category with no MFOEM class that is also absent from the OCC and GRID lists; it cannot be approximated by surprise (MFOEM:000032) because surprise lacks the vastness appraisal and is valence-neutral.
- **EDM usage:** `emotion.primary.text = "wonder"` coded to this class; currently `related: Cowen & Keltner awe`.

## 2. gratitude

- **Label:** gratitude
- **Parent:** emotion process (MFOEM:000001); positive emotion (MFOEM:000211).
- **Definition:** A positive emotion process directed at an agent, arising from the appraisal that the agent has intentionally conferred a benefit on oneself; combines approval of the agent's action with pleasure at the outcome.
- **Definition source:** Ortony, Clore & Collins (1988), compound well-being/attribution emotion gratitude = admiration + joy (`frameworks.json#occ`, verified against a secondary source in this pass); W3C EmotionML vocabularies Note (2014-04-01), `occ-categories#gratitude` (fetched); GoEmotions label `gratitude` (fetched).
- **Synonyms:** thankfulness, appreciation.
- **Why MFOEM needs it:** It is an OCC type, an EmotionML vocabulary item and a GoEmotions label, and one of the most frequent emotions in autobiographical and journaling text; MFOEM has admiration-like classes but no compound.
- **EDM usage:** canonical value `gratitude`; also an `arc_type` value since v0.8.0.

## 3. relief

- **Label:** relief
- **Parent:** emotion process (MFOEM:000001); positive emotion (MFOEM:000211).
- **Definition:** A positive emotion process arising when a feared or distressing goal-incongruent prospect is disconfirmed or a distressing condition ceases; the hedonic contrast of a removed threat.
- **Definition source:** Ortony, Clore & Collins (1988), prospect-based emotion relief (disconfirmed undesirable prospect); Lazarus (1991) core relational theme "a distressing goal-incongruent condition that has changed for the better or gone away" (`frameworks.json#lazarus`, fetched secondary); EmotionML `occ-categories#relief`; Geneva Emotion Wheel family Relief.
- **Synonyms:** reassurance (broad).
- **Why MFOEM needs it:** MFOEM encodes the appraisal side (appraisal of outcome probability) but has no emotion-process class for the resulting state; SNOMED CT has it (224978009 Feeling relief).
- **EDM usage:** canonical value `relief`.

## 4. nostalgia

- **Label:** nostalgia
- **Parent:** emotion process (MFOEM:000001); mixed valence (no MFOEM valence profile fits; propose none asserted).
- **Definition:** A sentimental longing for one's past, typically bittersweet: a positive affective core (warmth, social connectedness) accompanied by a sense of loss or irretrievability of the remembered period.
- **Definition source:** Sedikides, C. & Wildschut, T. (e.g. 2016, Review of General Psychology) [KNOWLEDGE: not fetched]; Cowen & Keltner (2017) category nostalgia (fetched); Hume taxonomy (fetched); Anthropic 2026 emotion-concept list contains "nostalgia" (fetched).
- **Synonyms:** longing (EDM canonical value, broad), yearning, sehnsucht (narrow).
- **Why MFOEM needs it:** It is the characteristic emotion of autobiographical recall, the domain EDM records; the ontology has no mixed-valence memory-directed class.
- **EDM usage:** `emotion.primary.text = "longing"` would code to this class; currently `related: Cowen & Keltner nostalgia`.

## 5. tenderness

- **Label:** tenderness
- **Parent:** emotion process (MFOEM:000001); positive emotion (MFOEM:000211). Not a subclass of love (MFOEM:000048), which MFOEM classifies as an emotion disposition; tenderness is the occurrent episode.
- **Definition:** A gentle, warm, caring emotion process directed at a person or creature perceived as vulnerable, dear or in need of protection, with an action tendency toward nurturance and closeness.
- **Definition source:** Lazarus (1991) core relational theme for love and compassion; GRID term "compassion"/"love" (knowledge-reconstructed); Panksepp CARE system (fetched secondary) as the proposed neural grounding; Kalawski (2010), "Is tenderness a basic emotion?", *Motivation and Emotion* 34 [KNOWLEDGE: not fetched].
- **Synonyms:** affection (broad), warmth.
- **Why MFOEM needs it:** EDM currently codes `tenderness` as `related` to love (disposition) and compassion (MFOEM:000052), neither of which is the episodic warm state; parental and caregiving memories need it.
- **EDM usage:** canonical value `tenderness`.

## 6. frustration

- **Label:** frustration
- **Parent:** emotion process (MFOEM:000001); negative emotion (MFOEM:000212 if present, else assert negative valence); sibling of anger (MFOEM:000009), not a subclass.
- **Definition:** A negative emotion process arising from the appraisal that progress toward a goal is blocked or delayed by an obstacle, without (or before) the attribution of blame to an agent that characterises anger.
- **Definition source:** Scherer's goal-conduciveness/obstructiveness check (CPM; `frameworks.json#scherer`); Russell (1980) circumplex word "frustrated" (verified in this pass); SNOMED CT 224973000 Feeling frustrated (verified on tx.fhir.org); Lazarus's distinction between frustration and anger by accountability [KNOWLEDGE].
- **Synonyms:** exasperation (narrow), thwarting.
- **Why MFOEM needs it:** MFOEM has anger and irritation-like classes but no goal-blockage state without blame; EDM's EU AI Act constraint forbids inferring blame, so subjects who say "frustrated" cannot be coded to anger.
- **EDM usage:** canonical value `frustration`.

## 7. wonder

- **Label:** wonder
- **Parent:** emotion process (MFOEM:000001); positive emotion (MFOEM:000211). If awe (request 1) is accepted, propose wonder as a sibling rather than a subclass: wonder is curiosity-weighted, awe is vastness-weighted.
- **Definition:** A positive emotion process elicited by the appraisal of something as novel, unexpected and not yet understood, combining surprise with sustained interest and a desire to explore or comprehend it.
- **Definition source:** Interest (MFOEM:000033) and surprise (MFOEM:000032) definitions in MFOEM itself; Keltner & Haidt (2003) distinguish wonder/curiosity-flavoured from threat-flavoured awe [KNOWLEDGE]; Plutchik dyads curiosity = trust + surprise and awe = fear + surprise (knowledge-reconstructed).
- **Synonyms:** marvel, amazement (Plutchik high-intensity surprise; broad).
- **Why MFOEM needs it:** EDM subjects use "wonder" far more often than "awe" in English journaling; coding it to interest or surprise drops either the novelty or the sustained-attention component.
- **EDM usage:** canonical value `wonder`.

---

## Filing notes

1. File as seven separate issues so each can be accepted independently; link them to one tracking issue titled "EDM canonical emotion values without MFOEM classes".
2. Offer the EDM vocabulary concept URIs (`https://emotionaldatamodel.org/vocab/emotion/v1#<value>`, proposed) as `oboInOwl:hasDbXref` targets once the namespace resolves.
3. Before filing, replace every [KNOWLEDGE] citation with a fetched one; the verification register in `REPORT.md` §9 lists what remains unverified.
