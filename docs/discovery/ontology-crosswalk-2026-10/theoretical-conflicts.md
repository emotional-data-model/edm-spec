# Theoretical conflicts across the reference set, and how EDM stays neutral

Discovery output, 2026-10-17. Sources are in `frameworks.json`; [KNOWLEDGE] marks claims not verified against a fetched source.

The neutrality mechanism proposed throughout is the one in `coding-proposal.md`: **an EDM field asserts an interpretation (`text`) and may carry several codings from incompatible systems; the artifact never asserts that one theory is true.** This is the same stance EmotionML took — it "does not prescribe a vocabulary" but lets each annotation point at a vocabulary URI (W3C EmotionML 1.0, fetched) — and it fits EDM's hard constraint that fields contain only what the source stated.

## 1. Basic emotions vs constructed emotion

- **Positions.** Ekman (6/7 universal emotions with distinct signals; paulekman.com, fetched), Panksepp (seven subcortical primary-process systems), Plutchik (eight primaries with opposites and intensities) hold that a small set of emotion kinds is given by biology. Barrett 2017 (fetched) holds that emotion categories are constructed by the brain from core affect (valence, arousal) plus concepts; categories are populations of variable instances, not natural kinds. Cowen & Keltner 2017 (fetched) sit between: 27 categories but with continuous gradients and blends.
- **Where EDM currently leans.** A closed-ish canonical list of 17 reads as a basic-emotion claim, and `narrative_archetype` reads as a Jungian claim.
- **Neutral position.** `emotion.primary.text` is the subject's own word (constructionist: the category the person used). Codings to MFOEM / EmotionML / GoEmotions give basic-emotion consumers their labels without the spec asserting them. The canonical list becomes a *recommended* vocabulary, not an enum. Record `valence` and `arousal` separately so that a core-affect reading is always available even when no category is coded.

## 2. Discrete categories vs dimensions

- **Positions.** Russell 1980 circumplex and Mehrabian PAD describe affect by two or three continuous dimensions; Fontaine, Scherer, Roesch & Ellsworth 2007 (abstract fetched) show four dimensions (valence, potency/control, arousal, unpredictability) are needed; category theorists treat dimensions as derived.
- **Where EDM currently leans.** Categorical. Only valence (3-way) and intensity exist; arousal and unpredictability are absent (gap list B).
- **Neutral position.** Add `emotion.arousal`; keep `valence`, `intensity`, `appraisal.control` as numeric-capable dimensions coded to EmotionML `pad-dimensions` / `fsre-dimensions`. EmotionML already allows `<category>` and `<dimension>` in the same `<emotion>`; EDM should mirror that so one interpretation has both views.

## 3. Appraisal theories vs affect programs

- **Positions.** Scherer CPM, Lazarus 1991 and OCC derive the emotion from an evaluation of the situation (novelty, goal conduciveness, coping potential, norm compatibility; core relational themes; prospect/attribution/attraction). Affect-program theories (Ekman, Panksepp) treat the emotion as triggered pattern first, appraisal second. MFOEM encodes appraisals as separate classes (`MFOEM:000005` affective appraisal) that *accompany* an emotion process rather than define it.
- **Where EDM currently leans.** Mixed: `spark`, `urgency`, `agency_level`, `risk_posture` are appraisal-shaped; `emotion_primary` is label-shaped; nothing says whether one derives from the other.
- **Neutral position.** Group the appraisal-shaped fields under `emotion.appraisal.*`, code them to MFOEM / EmotionML `scherer-appraisals`, and state in the spec that appraisal fields are recorded only when the subject expressed them and are never used to infer the emotion label (this is also what the EU AI Act constraint already demands).

## 4. Emotion vs mood vs feeling vs disposition

- **Positions.** MFOEM distinguishes emotion process, mood process, subjective affective feeling, emotion disposition (love, hate) and trait. Damasio distinguishes emotion (bodily) from feeling (perception of the body state) and background emotions [KNOWLEDGE]. Scherer separates emotion from mood by duration and object-focus [KNOWLEDGE].
- **Where EDM currently leans.** `viscosity=enduring` and `temporal_decay` are the only hint that something is mood-like; `tenderness` and `love` are dispositions in MFOEM but appear as emotion values.
- **Neutral position.** Add `emotion.kind` with codes `MFOEM:000001` emotion process | `MFOEM:000193` mood process | `MFOEM:000006` subjective affective feeling | `MFOEM:000199` emotion disposition. Default to emotion process when the subject does not distinguish.

## 5. Event-level description vs person-level trait

- **Positions.** Attachment classifications (Ainsworth, Bartholomew), emotional intelligence (Mayer–Salovey, Goleman, Bar-On), Barrett's granularity, Elliot's temperaments and SDT causality orientations are properties of a person measured by instruments, not of a single experience. Lazarus, Pillemer, Singer & Blagov and McAdams code individual memories or encounters.
- **Where EDM currently leans.** `attachment_style`, `regulation_state`, `resilience_markers` and `risk_posture` can be read as trait labels; `SCOPE_AND_NONGOALS.md` already forbids inferring attachment.
- **Neutral position.** Keep all fields event-scoped and say so in each description ("as stated for this experience"). Do not add EI or granularity fields. Person-level aggregation, if ever wanted, is a downstream analytic outside the artifact.

## 6. Literary narrative structure vs empirical narrative identity

- **Positions.** Booker (seven plots) and Campbell (17 stages) are literary-critical taxonomies of stories; McAdams, Singer & Blagov and Pillemer are empirically coded features of personal memories (redemption, contamination, integrative meaning, turning points). Bruner argues narrative is a mode of thought with ten features, not a plot catalogue.
- **Where EDM currently leans.** `arc_type` mixes both (grief, gratitude are emotions; threshold, exile are Campbell stages; transformation is a Booker plot; moral_awakening is McAdams-like).
- **Neutral position.** Keep one `narrative.arc` list with provenance per value in the vocabulary file, and allow multiple arc codings (a Booker reading and a McAdams reading of the same memory can both be stored). Move pure emotions out of the arc list.

## 7. Memory-type taxonomies

- **Positions.** Conway: lifetime periods / general events / event-specific knowledge (structural levels). Pillemer: originating, turning-point, anchoring, analogous events (functional types). Singer & Blagov: specific vs summary, integrative vs non-integrative (coding dimensions). Tulving: episodic vs semantic (systems).
- **Where EDM currently leans.** `memory_type` is a bespoke five-value mixture; `recurrence_pattern` and `temporal_context` carry Conway-like information elsewhere.
- **Neutral position.** `salience.memory_type` takes Pillemer's functional types; `salience.recurrence` carries Singer specificity; `context.life_stage` carries the Conway level. Three fields, three theories, no field claims to be the taxonomy.

## 8. Semantic-space (gradient) models vs fixed lists

- **Positions.** Cowen & Keltner and Hume AI model emotion as a high-dimensional space with blends; GoEmotions is multi-label; Plutchik has dyads. Fixed lists (Ekman, GEW) assign one label.
- **Neutral position.** `emotion.secondary[]` with per-coding `confidence` (EmotionML attribute) gives the blended view; `emotion.primary` gives the single-label view. Note that Cowen & Keltner's own paper is internally inconsistent about whether pride or relief is in the 27 (fetched; see `frameworks.json#cowen_keltner`).

## 9. Transactional coping vs process-model regulation

- **Positions.** Lazarus & Folkman classify coping by its function in a stressful transaction (eight Ways of Coping scales, fetched); Gross classifies regulation by *when* in the emotion-generative process it acts (five families) [KNOWLEDGE].
- **Neutral position.** `motivation.coping` may carry both a Ways-of-Coping coding and a Gross-family coding; the two are orthogonal, not competing, for most values (positive reappraisal = cognitive change; escape-avoidance ≈ attentional deployment / situation selection).

## 10. Functional emotion concepts in language models (Anthropic 2026)

- **Position.** The Anthropic interpretability post and paper "Emotion concepts and their function in a large language model" (fetched; 171 emotion words, Claude Sonnet 4.5) describe representations inside a model, not a theory of human emotion. The authors frame them as functional emotion *concepts* and avoid claims about experience.
- **Neutral position.** EDM should not adopt the 171 words as a normative vocabulary. They are relevant as an interpretability cross-reference: an extraction engine built on a Claude model can be audited by checking whether the emotion it writes into `emotion.primary` corresponds to one of these concepts. Keep the mapping in `crosswalks` or telemetry, not in the affective core.

## 11. Collective vs individual memory

- **Position.** Everything in the reference set is individual-level; ritual, tradition and commemorative memory (Durkheim; Halbwachs 1925; Connerton 1989) [KNOWLEDGE] are not represented, yet EDM's `tether_type=ritual|tradition` and `relational_dynamics=community_ritual` point at them.
- **Neutral position.** Keep the values and mark them EDM-specific with a collective-memory citation in the vocabulary file; this is the one area where the reference set, not EDM, is incomplete.
