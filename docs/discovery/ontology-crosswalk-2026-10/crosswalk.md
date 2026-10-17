# EDM v0.8.3 ontology crosswalk

Generated 2026-10-17 from `fields.json` (57 fields, 185 canonical values) against 39 framework columns. Discovery output only; nothing normative.

## Legend

Relation direction is EDM -> target.

| Relation | Meaning |
|---|---|
| exact | same concept (label may differ) |
| broader | target is broader than the EDM concept |
| narrower | target is narrower than the EDM concept |
| related | overlapping or associated; neither subsumes the other |
| none | no mapping (cells omitted from the tables below; full matrix in `crosswalk.csv`) |

Verification flag on each target: **V** = target label found in a value list fetched from the framework's source; **K** = found only in a list reconstructed from model knowledge ([KNOWLEDGE]); **-** = free-form target (structural description, element name or paraphrase) not checkable against a value list. See `frameworks.json` for per-construct `value_source`.

Grounding per row: **strong** = at least one exact mapping; **moderate** = broader/narrower only; **weak** = related only; **orphan** = no mapping.

## Summary

| Measure | Count |
|---|---|
| Field rows | 57 |
| Value rows | 185 |
| Mappings | 913 |
| Targets verified V / K / - | 393 / 241 / 279 |
| Fields strong / moderate / weak / orphan | 19 / 1 / 36 / 1 |
| Values strong / moderate / weak / orphan | 62 / 0 / 96 / 27 |

| Domain | Fields | strong | weak | orphan | Values | strong | orphan |
|---|---|---|---|---|---|---|---|
| core | 7 | 1 | 6 | 0 | 0 | 0 | 0 |
| constellation | 19 | 6 | 13 | 0 | 102 | 31 | 10 |
| milky_way | 5 | 1 | 3 | 1 | 3 | 0 | 3 |
| gravity | 14 | 4 | 10 | 0 | 32 | 7 | 9 |
| impulse | 12 | 7 | 4 | 0 | 48 | 24 | 5 |

### Framework coverage (rows touched / exact mappings)

| Framework | Family | Rows touched | Exact |
|---|---|---|---|
| Ekman basic emotions | emotion | 10 | 5 |
| Plutchik wheel | emotion | 28 | 11 |
| Cowen & Keltner 2017 | emotion | 25 | 7 |
| GoEmotions | emotion | 23 | 15 |
| Russell circumplex | emotion | 19 | 6 |
| PAD (Mehrabian & Russell) | emotion | 17 | 7 |
| OCC | emotion | 30 | 17 |
| Scherer CPM / GRID / GEW | emotion | 30 | 16 |
| Barrett constructed emotion | emotion | 8 | 2 |
| Anthropic 2026 emotion concepts | emotion | 17 | 12 |
| Hume semantic space | emotion | 21 | 11 |
| Panksepp primary systems | salience | 36 | 5 |
| Damasio | salience | 6 | 1 |
| Conway self-memory system | salience | 38 | 3 |
| Singer & Blagov SDM | salience | 36 | 7 |
| Pillemer momentous events | salience | 25 | 3 |
| Lazarus appraisal / coping | salience | 58 | 20 |
| McAdams narrative identity | narrative | 82 | 7 |
| Bruner | narrative | 5 | 0 |
| Booker seven plots | narrative | 20 | 4 |
| Campbell monomyth | narrative | 19 | 3 |
| Tulving episodic memory | narrative | 19 | 6 |
| Ainsworth / Main attachment | context | 11 | 6 |
| Bartholomew adult attachment | context | 7 | 1 |
| Fiske relational models | context | 24 | 0 |
| Bronfenbrenner ecological systems | context | 28 | 3 |
| Gross process model | motivation | 19 | 3 |
| Elliot approach-avoidance | motivation | 12 | 3 |
| Self-determination theory | motivation | 12 | 4 |
| Mayer-Salovey EI | motivation | 4 | 0 |
| Goleman EI | motivation | 6 | 0 |
| Bar-On EQ-i | motivation | 10 | 0 |
| W3C EmotionML + vocabularies | machine | 54 | 23 |
| OBO MFOEM Emotion Ontology | machine | 57 | 25 |
| HUMAINE EARL | machine | 21 | 19 |
| WordNet-Affect | machine | 23 | 14 |
| NRC lexicons | machine | 17 | 9 |
| SenticNet Hourglass | machine | 19 | 11 |
| SNOMED CT | machine | 16 | 9 |

## Matrix by domain


## CORE


### `core.anchor` — free_text — grounding: **weak**

_Central person, object, or theme of the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference role="targetedAt"> | - | object/person the emotion is about |
| OCC | related | aspects of objects / actions of agents (eliciting branches) | K | the thing the valenced reaction is about |
| Singer & Blagov SDM | related | content category (relationship, achievement, ...) | K | content domain of the memory |
| Conway self-memory system | related | general event / ESK theme | - | thematic index in the autobiographical knowledge base |
| Lazarus appraisal / coping | related | ego-involvement (type) | V | what is at stake |

### `core.spark` — free_text — grounding: **strong**

_What triggered or initiated the emotional response_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | exact | <reference role="triggeredBy"> | - | the trigger of the emotion |
| Lazarus appraisal / coping | related | primary appraisal: encounter / stimulus event | V | eliciting encounter |
| Scherer CPM / GRID / GEW | related | eliciting event; relevance check (novelty) | - | CPM first SEC |
| OCC | related | eliciting event / agent / object | - | OCC root branches |
| Gross process model | related | situation (situation selection / modification) | K | the situation that elicits |
| Pillemer momentous events | related | originating event | - | event that starts a life path |
| OBO MFOEM Emotion Ontology | related | affective appraisal process (MFOEM:000002) | V | MFOEM models the appraisal, not the stimulus |

### `core.wound` — free_text — grounding: **weak**

_Emotional pain, loss, or vulnerability present in the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | harm/loss appraisal; core relational theme: sadness (irrevocable loss) | - |  |
| OBO MFOEM Emotion Ontology | related | appraisal of loss (MFOEM:000106) | V |  |
| Conway self-memory system | related | SDM criterion: enduring concern / unresolved conflict | K |  |
| Singer & Blagov SDM | related | content: life-threatening events; guilt/shame | K |  |
| McAdams narrative identity | related | contamination sequence; low point | K |  |
| Scherer CPM / GRID / GEW | related | goal conduciveness / obstructiveness check | - |  |
| Panksepp primary systems | related | PANIC/GRIEF | V |  |

### `core.fuel` — free_text — grounding: **weak**

_What energized or motivated the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Panksepp primary systems | related | SEEKING | V | generic appetitive motivation |
| Self-determination theory | related | intrinsic motivation; basic psychological needs | V |  |
| Elliot approach-avoidance | related | approach motivation | - |  |
| Lazarus appraisal / coping | related | goal relevance (primary appraisal) | V |  |
| Scherer CPM / GRID / GEW | related | goal conduciveness | - |  |
| McAdams narrative identity | related | agency / communion themes | K |  |

### `core.bridge` — free_text — grounding: **weak**

_Connection or shift between past and present understanding_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | meaning-making; redemption sequence | K | link between past event and present understanding |
| Singer & Blagov SDM | related | integrative meaning | K |  |
| Conway self-memory system | related | coherence (self-memory system) | K |  |
| Tulving episodic memory | related | chronesthesia / mental time travel | K |  |

### `core.echo` — free_text — grounding: **weak**

_What continues to resonate or recur from the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Pillemer momentous events | related | sensory imagery; vividness of personal event memory | - |  |
| Conway self-memory system | related | SDM criterion: vividness; rehearsal | K |  |
| Singer & Blagov SDM | related | SDM criterion: repeatedly recalled | - |  |
| Tulving episodic memory | related | encoding specificity (retrieval cue) | K |  |

### `core.narrative` — free_text — grounding: **weak**

_A compressed, faithful account of the experience as described by the source, preserving emotional sequence, temporal markers, and stated context without interpretation_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | life-story episode narrative (nuclear episode) | - |  |
| Bruner | related | narrative mode; particularity; diachronicity | K |  |
| Tulving episodic memory | related | episodic memory (what-where-when) | K |  |
| Singer & Blagov SDM | related | specificity: specific (single-event) memory | K |  |
| Pillemer momentous events | related | personal event memory | K |  |

## CONSTELLATION


### `constellation.emotion_primary` — canonical_open — grounding: **strong**

_The dominant emotional quality expressed in the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | related | basic emotion category set | - | EDM 17 vs Ekman 6/7 |
| Plutchik wheel | related | 8 primary emotions x 3 intensities | - |  |
| Cowen & Keltner 2017 | related | 27 emotion categories | - |  |
| GoEmotions | related | 27 labels + neutral | - |  |
| Russell circumplex | related | 28 circumplex affect terms | - |  |
| PAD (Mehrabian & Russell) | related | 8 PAD octant labels | - |  |
| OCC | related | 22 emotion types | - |  |
| Scherer CPM / GRID / GEW | related | GRID 24 terms / GEW 20 families | K |  |
| Barrett constructed emotion | related | emotion concept / category (constructed) | - | Barrett: category is a population, not a natural kind |
| Anthropic 2026 emotion concepts | related | emotion concepts (171) | V | functional emotion concepts in Claude Sonnet 4.5 |
| Hume semantic space | related | expression categories | - |  |
| Panksepp primary systems | related | primary-process emotional systems | V |  |
| Damasio | related | primary / secondary emotions | K |  |
| Lazarus appraisal / coping | related | core relational themes (one per emotion) | V |  |
| W3C EmotionML + vocabularies | exact | <category name= set=...> | - | single categorical label; set = vocabulary URI |
| OBO MFOEM Emotion Ontology | exact | emotion process (MFOEM:000001) subclass | - | artifact field = instance of an emotion-process class |
| HUMAINE EARL | exact | <emotion category=...> | - | EARL predecessor of EmotionML |
| WordNet-Affect | related | emotion a-label hierarchy | - |  |
| NRC lexicons | related | EmoLex 8 emotions | - |  |
| SenticNet Hourglass | related | Hourglass sentic levels | - |  |
| SNOMED CT | related | Emotion (observable entity) / emotional state finding | V | see frameworks.json for SCTIDs |

**`joy`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | exact | enjoyment (happiness) | V |  |
| Plutchik wheel | exact | joy | V |  |
| Cowen & Keltner 2017 | exact | joy | V |  |
| GoEmotions | exact | joy | V |  |
| OCC | exact | joy | K |  |
| Scherer CPM / GRID / GEW | exact | joy (GRID/GEW) | K |  |
| Russell circumplex | related | happy / delighted (high pleasure, mid arousal) | K |  |
| PAD (Mehrabian & Russell) | related | +P +A +D exuberant | - |  |
| Panksepp primary systems | related | PLAY | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000034 joy | V |  |
| W3C EmotionML + vocabularies | exact | big6#happiness; everyday-categories#happy; fsre-categories#joy | V |  |
| HUMAINE EARL | exact | Joy | V |  |
| WordNet-Affect | exact | joy | V |  |
| NRC lexicons | exact | joy | V |  |
| SenticNet Hourglass | exact | joy (Pleasantness level 2012; Introspection level 2020) | V |  |
| SNOMED CT | related | 112080002 Cheerful mood (finding) [synonym Happiness]; 34822003 Elation (finding) | V | no exact SNOMED concept for joy |
| Hume semantic space | exact | Joy | V |  |
| Lazarus appraisal / coping | exact | happiness: making reasonable progress toward a goal | V |  |
| Anthropic 2026 emotion concepts | exact | joyful | V | 171-word set |

**`sadness`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | exact | sadness | V |  |
| Plutchik wheel | exact | sadness | V |  |
| Cowen & Keltner 2017 | exact | sadness | V |  |
| GoEmotions | exact | sadness | V |  |
| OCC | exact | distress | K |  |
| Scherer CPM / GRID / GEW | exact | sadness | K |  |
| Russell circumplex | related | sad / gloomy (low pleasure, low arousal) | K |  |
| PAD (Mehrabian & Russell) | related | -P -A (no octant label) | K |  |
| Panksepp primary systems | broader | PANIC/GRIEF | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000056 sadness | V |  |
| W3C EmotionML + vocabularies | exact | big6#sadness; fsre-categories#sadness; everyday-categories#sad | V |  |
| HUMAINE EARL | exact | Sadness | V |  |
| WordNet-Affect | exact | sadness | V |  |
| NRC lexicons | exact | sadness | V |  |
| SenticNet Hourglass | exact | sadness (Pleasantness level 2012; Introspection level 2020) | V |  |
| SNOMED CT | exact | 420038007 Feeling unhappy (finding) | V |  |
| Hume semantic space | exact | Sadness | V |  |
| Lazarus appraisal / coping | exact | sadness: having experienced an irrevocable loss | V |  |
| Anthropic 2026 emotion concepts | exact | sad | V |  |

**`fear`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | exact | fear | V |  |
| Plutchik wheel | exact | fear | V |  |
| Cowen & Keltner 2017 | exact | fear | V |  |
| GoEmotions | exact | fear | V |  |
| OCC | exact | fear | K |  |
| Scherer CPM / GRID / GEW | exact | fear | K |  |
| Russell circumplex | related | afraid / alarmed (low pleasure, high arousal) | K |  |
| PAD (Mehrabian & Russell) | related | -P +A -D anxious | - |  |
| Panksepp primary systems | exact | FEAR | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000026 fear | V |  |
| W3C EmotionML + vocabularies | exact | big6#fear; fsre-categories#fear; everyday-categories#afraid | V |  |
| HUMAINE EARL | exact | Fear | V |  |
| WordNet-Affect | exact | fear | V |  |
| NRC lexicons | exact | fear | V |  |
| SenticNet Hourglass | exact | fear (Sensitivity level) | V |  |
| SNOMED CT | exact | 1402001 Fear (finding) | V |  |
| Hume semantic space | exact | Fear | V |  |
| Lazarus appraisal / coping | exact | fright: facing an immediate, concrete, overwhelming physical danger | V |  |
| Anthropic 2026 emotion concepts | exact | afraid; frightened; scared | V |  |

**`anger`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | exact | anger | V |  |
| Plutchik wheel | exact | anger | V |  |
| Cowen & Keltner 2017 | exact | anger | V |  |
| GoEmotions | exact | anger | V |  |
| OCC | exact | anger | K |  |
| Scherer CPM / GRID / GEW | exact | anger | K |  |
| Russell circumplex | exact | angry | K |  |
| PAD (Mehrabian & Russell) | related | -P +A +D hostile | - |  |
| Panksepp primary systems | exact | RAGE | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000009 anger | V |  |
| W3C EmotionML + vocabularies | exact | big6#anger; fsre-categories#anger; everyday-categories#angry | V |  |
| HUMAINE EARL | exact | Anger | V |  |
| WordNet-Affect | exact | anger | V |  |
| NRC lexicons | exact | anger | V |  |
| SenticNet Hourglass | exact | anger (Sensitivity level 2012; Temper level 2020) | V |  |
| SNOMED CT | exact | 75408008 Feeling angry (finding) | V |  |
| Hume semantic space | exact | Anger | V |  |
| Lazarus appraisal / coping | exact | anger: a demeaning offense against me and mine | V |  |
| Anthropic 2026 emotion concepts | exact | angry | V |  |

**`wonder`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | related | surprise | V |  |
| Plutchik wheel | related | awe (primary dyad fear + surprise); surprise | V |  |
| Cowen & Keltner 2017 | related | awe; interest; surprise | V |  |
| GoEmotions | related | surprise; curiosity; admiration | V |  |
| Scherer CPM / GRID / GEW | related | surprise; interest (GRID) | K |  |
| Russell circumplex | related | astonished | K |  |
| Panksepp primary systems | related | SEEKING | V |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000209 positive surprise; MFOEM:000167 curiosity; MFOEM:000033 interest | V |  |
| W3C EmotionML + vocabularies | related | big6#surprise; everyday-categories#interested; fsre-categories#interest | V |  |
| HUMAINE EARL | related | Interest; Surprise | V |  |
| WordNet-Affect | related | surprise; wonder (under surprise) | V | WordNet-Affect places "wonder" synsets under surprise [KNOWLEDGE] |
| NRC lexicons | related | surprise; anticipation | V |  |
| SenticNet Hourglass | related | awe (2012 compound Sensitivity<0 x Attention<0); amazement; surprise (Attention levels) | V |  |
| Hume semantic space | related | Awe; Interest; Surprise (positive) | V |  |
| Anthropic 2026 emotion concepts | related | awestruck; amazed | V | no "wonder" in the 171 set |

**`peace`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | exact | serenity (low-intensity joy) | K |  |
| Cowen & Keltner 2017 | exact | calmness | V |  |
| Scherer CPM / GRID / GEW | related | contentment (GRID/GEW) | K |  |
| Russell circumplex | exact | calm / relaxed / serene / at ease | K |  |
| PAD (Mehrabian & Russell) | related | +P -A +D relaxed | - |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000043 serenity; MFOEM:000114 feeling calm | V |  |
| W3C EmotionML + vocabularies | related | everyday-categories#relaxed; everyday-categories#content; fsre-categories#contentment | V |  |
| HUMAINE EARL | exact | Calm; Serene | V |  |
| WordNet-Affect | related | calmness (positive-emotion) | - |  |
| SenticNet Hourglass | exact | serenity (Pleasantness level 2012); calmness; serenity (Temper levels 2020) | V |  |
| Hume semantic space | exact | Calmness | V |  |
| Anthropic 2026 emotion concepts | exact | peaceful; calm; serene | V |  |
| SNOMED CT | related | 102894008 Feeling calm (finding); 271599002 Feeling content (finding) | V | no exact SNOMED concept for peace |

**`tenderness`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | related | love (primary dyad joy + trust); trust | V |  |
| Cowen & Keltner 2017 | related | adoration; sympathy (rated set); romance | V |  |
| GoEmotions | related | caring; love | V |  |
| OCC | related | love (liking) | K |  |
| Scherer CPM / GRID / GEW | related | compassion; love (GRID) | K |  |
| Panksepp primary systems | exact | CARE | V |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000052 compassion; MFOEM:000049 companionate love | V |  |
| W3C EmotionML + vocabularies | related | fsre-categories#love; everyday-categories#affectionate; everyday-categories#loving | V |  |
| HUMAINE EARL | related | Affection; Love | V |  |
| WordNet-Affect | related | love / affection | - |  |
| NRC lexicons | related | trust | V |  |
| SenticNet Hourglass | related | love (2012 compound Pleasantness>0 x Aptitude>0); admiration; trust (Aptitude levels) | V |  |
| SNOMED CT | related | 23682002 Love (finding) | V | all SNOMED "Tenderness" concepts are palpation findings |
| Hume semantic space | related | Love; Adoration; Sympathy | V |  |
| Lazarus appraisal / coping | related | compassion; love | V |  |
| Anthropic 2026 emotion concepts | related | loving; compassionate | V | no "tender" in the 171 set |

**`reverence`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Cowen & Keltner 2017 | related | awe; admiration | V |  |
| GoEmotions | related | admiration | V |  |
| OCC | related | admiration | K |  |
| SenticNet Hourglass | related | admiration (Aptitude) | V |  |
| Hume semantic space | related | Admiration; Awe | V |  |
| WordNet-Affect | related | reverence / veneration (under love/respect) | - | [KNOWLEDGE] low confidence |
| Anthropic 2026 emotion concepts | related | awestruck | V | no "reverence" in the 171 set |

**`pride`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | related | pride in achievement (1999 expanded list) | K |  |
| Cowen & Keltner 2017 | related | pride (rated 34 set; dropped from final 27, co-loaded with admiration/triumph) | V |  |
| Plutchik wheel | related | pride (secondary dyad anger + joy) | K |  |
| GoEmotions | exact | pride | V |  |
| OCC | exact | pride | K |  |
| Scherer CPM / GRID / GEW | exact | pride | K |  |
| PAD (Mehrabian & Russell) | related | +D dominance | - |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000041 pride | V |  |
| W3C EmotionML + vocabularies | exact | fsre-categories#pride; occ-categories#pride | V |  |
| HUMAINE EARL | exact | Pride | V |  |
| WordNet-Affect | exact | pride | - |  |
| Hume semantic space | exact | Pride | V |  |
| SenticNet Hourglass | related | pride (2020 Attitude-toward-self, PLEASANTNESS level) | V |  |
| SNOMED CT | exact | 1149081002 Feeling proud (finding) | V |  |
| Lazarus appraisal / coping | exact | pride: enhancement of ego-identity by taking credit for a valued object or achievement | V |  |
| Anthropic 2026 emotion concepts | exact | proud | V |  |

**`anxiety`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | related | fear | V |  |
| Plutchik wheel | exact | anxiety (tertiary dyad anticipation + fear); apprehension | K |  |
| Cowen & Keltner 2017 | exact | anxiety | V |  |
| GoEmotions | exact | nervousness | V |  |
| OCC | broader | fear | K |  |
| Scherer CPM / GRID / GEW | exact | anxiety (GRID) | K |  |
| Russell circumplex | related | tense / nervous | K |  |
| PAD (Mehrabian & Russell) | exact | -P +A -D anxious | - |  |
| Panksepp primary systems | broader | FEAR | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000028 anxiety; MFOEM:000196 anxious mood | V |  |
| W3C EmotionML + vocabularies | exact | fsre-categories#anxiety; everyday-categories#worried | V |  |
| HUMAINE EARL | exact | Anxiety; Worry | V |  |
| WordNet-Affect | exact | anxiety | - |  |
| NRC lexicons | broader | fear | V |  |
| SenticNet Hourglass | exact | anxiety (2020 Sensitivity level; 2012 compound Sensitivity<0 x Attention>0); apprehension | V |  |
| SNOMED CT | exact | 48694002 Anxiety (finding) | V |  |
| Hume semantic space | exact | Anxiety | V |  |
| Lazarus appraisal / coping | exact | anxiety: facing uncertain, existential threat | V |  |
| Anthropic 2026 emotion concepts | exact | anxious | V |  |

**`gratitude`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| GoEmotions | exact | gratitude | V |  |
| OCC | exact | gratitude | K |  |
| W3C EmotionML + vocabularies | exact | occ-categories#gratitude | V |  |
| WordNet-Affect | exact | gratitude | - |  |
| Hume semantic space | exact | Gratitude | - | check Hume list |
| Lazarus appraisal / coping | exact | gratitude: appreciation for an altruistic gift that provides personal benefit | - |  |
| Anthropic 2026 emotion concepts | exact | grateful; thankful | V |  |

**`longing`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Cowen & Keltner 2017 | related | craving; nostalgia | V |  |
| GoEmotions | related | desire | V |  |
| Panksepp primary systems | related | SEEKING; PANIC/GRIEF (separation) | V |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000220 feeling of desire; MFOEM:000221 feeling of want | V |  |
| WordNet-Affect | related | desire / yearning | - |  |
| W3C EmotionML + vocabularies | related | frijda-categories#desire | V |  |
| NRC lexicons | related | anticipation | V |  |
| Hume semantic space | related | Craving; Desire; Nostalgia | V |  |
| Anthropic 2026 emotion concepts | related | nostalgic | V | no "longing" in the 171 set |

**`hope`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | exact | hope (secondary dyad anticipation + trust); optimism (primary dyad) | K |  |
| GoEmotions | exact | optimism | V |  |
| OCC | exact | hope | K |  |
| Panksepp primary systems | related | SEEKING | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000177 hope | V |  |
| W3C EmotionML + vocabularies | exact | occ-categories#hope | V |  |
| HUMAINE EARL | exact | Hope | V |  |
| WordNet-Affect | exact | hope | - |  |
| NRC lexicons | related | anticipation | V |  |
| SenticNet Hourglass | related | optimism (2012 compound Pleasantness>0 x Attention>0) | V |  |
| SNOMED CT | exact | 225649001 Hopeful for the future (finding) | V | also 247797001 Level of hope (observable entity) |
| Lazarus appraisal / coping | exact | hope: fearing the worst but yearning for better | V |  |
| Anthropic 2026 emotion concepts | exact | hope; hopeful | V |  |

**`shame`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | related | shame (1999 expanded list) | K |  |
| Cowen & Keltner 2017 | related | awkwardness | V |  |
| Plutchik wheel | related | shame (tertiary dyad fear + disgust) | K |  |
| GoEmotions | related | embarrassment; remorse | V |  |
| OCC | exact | shame | K |  |
| Scherer CPM / GRID / GEW | exact | shame | K |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000055 shame | V |  |
| W3C EmotionML + vocabularies | exact | occ-categories#shame; fsre-categories#shame | V |  |
| HUMAINE EARL | exact | Shame | V |  |
| WordNet-Affect | exact | shame | - |  |
| SenticNet Hourglass | related | shame (2020 Attitude-toward-self, DISGUST level) | V |  |
| SNOMED CT | exact | 225012006 Feeling ashamed (finding) | V |  |
| Hume semantic space | exact | Shame | V |  |
| Lazarus appraisal / coping | exact | shame: having failed to live up to an ego-ideal | V |  |
| Anthropic 2026 emotion concepts | exact | ashamed | V |  |

**`disappointment`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | related | sadness; disapproval (primary dyad surprise + sadness) | V |  |
| Cowen & Keltner 2017 | related | disappointment (rated 34 set; not in final 27) | V |  |
| GoEmotions | exact | disappointment | V |  |
| OCC | exact | disappointment | K |  |
| Scherer CPM / GRID / GEW | exact | disappointment | K |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000051 disappointment | V |  |
| W3C EmotionML + vocabularies | exact | occ-categories#disappointment; fsre-categories#disappointment; everyday-categories#disappointed | V |  |
| HUMAINE EARL | exact | Disappointment | V |  |
| WordNet-Affect | related | disappointment (under sadness) | - |  |
| Hume semantic space | exact | Disappointment | V |  |

**`relief`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ekman basic emotions | exact | relief (1999 expanded list) | K |  |
| Cowen & Keltner 2017 | exact | relief | V | see Cowen & Keltner inconsistency note |
| GoEmotions | exact | relief | V |  |
| OCC | exact | relief | K |  |
| Scherer CPM / GRID / GEW | exact | relief (GEW) | K |  |
| W3C EmotionML + vocabularies | exact | occ-categories#relief | V |  |
| HUMAINE EARL | exact | Relieved | V |  |
| WordNet-Affect | related | relief (positive-emotion) | - |  |
| Hume semantic space | exact | Relief | V |  |
| SNOMED CT | exact | 224978009 Feeling relief (finding) | V |  |
| Lazarus appraisal / coping | exact | relief: a distressing goal-incongruent condition that has changed for the better or gone away | V |  |
| Anthropic 2026 emotion concepts | exact | relieved | V |  |

**`frustration`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | related | annoyance; anger | V |  |
| GoEmotions | related | annoyance; anger | V |  |
| OCC | related | anger; distress | K |  |
| Scherer CPM / GRID / GEW | related | irritation (GRID) | K |  |
| Russell circumplex | exact | frustrated | K |  |
| PAD (Mehrabian & Russell) | related | -P +A | K |  |
| Panksepp primary systems | related | RAGE (SEEKING frustration) | V |  |
| OBO MFOEM Emotion Ontology | broader | MFOEM:000009 anger; related MFOEM:000011 irritation, MFOEM:000012 annoyance | V |  |
| W3C EmotionML + vocabularies | related | fsre-categories#irritation | V |  |
| HUMAINE EARL | exact | Frustration | V |  |
| WordNet-Affect | related | frustration (under anger) | - |  |
| NRC lexicons | broader | anger | V |  |
| SenticNet Hourglass | exact | frustration (2012 compound Pleasantness<0 x Attention>0); annoyance (level) | V |  |
| Hume semantic space | related | Annoyance | - |  |
| SNOMED CT | exact | 224973000 Feeling frustrated (finding) | V |  |
| Lazarus appraisal / coping | related | anger | V |  |
| Anthropic 2026 emotion concepts | exact | frustrated | V |  |

### `constellation.emotion_subtone` — free_text_list — grounding: **strong**

_Secondary emotional nuances that add depth to the primary emotion_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | exact | multiple <category> / multiple <emotion> with confidence | - | EmotionML allows several categories per annotation |
| HUMAINE EARL | exact | <complex-emotion> container | - |  |
| Plutchik wheel | related | dyads (primary/secondary/tertiary) | K | mixed emotions |
| Cowen & Keltner 2017 | related | blends / continuous gradients between categories | V |  |
| GoEmotions | related | multi-label annotation | - |  |
| Barrett constructed emotion | related | emotional granularity | K |  |
| Hume semantic space | related | multi-dimensional expression scores | - |  |
| OBO MFOEM Emotion Ontology | related | co-occurring emotion processes | - |  |

### `constellation.higher_order_emotion` — free_text — grounding: **weak**

_Complex or layered emotional state_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Cowen & Keltner 2017 | related | awe; aesthetic appreciation; nostalgia; entrancement | V | complex self-transcendent categories |
| Damasio | related | secondary (social) emotions | - |  |
| OCC | related | compound emotions (gratification, remorse, gratitude, anger) | - |  |
| Plutchik wheel | related | dyads | K |  |
| Barrett constructed emotion | related | conceptual combination | - |  |
| Hume semantic space | related | Awe; Aesthetic Appreciation; Nostalgia | V |  |

### `constellation.meta_emotional_state` — free_text — grounding: **weak**

_How the person relates to their own emotional state_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Gross process model | related | extended process model: identification stage (emotion awareness / valuation) | K |  |
| Mayer-Salovey EI | related | branch 4: reflective regulation (openness to feelings) | - |  |
| Goleman EI | related | emotional self-awareness | V |  |
| Bar-On EQ-i | related | emotional self-awareness subscale | - |  |

### `constellation.interpersonal_affect` — free_text — grounding: **weak**

_Emotional posture in relational context_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | enacted relational model | - |  |
| Goleman EI | related | social awareness / relationship management | V |  |
| Bar-On EQ-i | related | interpersonal composite (empathy, interpersonal relationship) | - |  |
| Mayer-Salovey EI | related | managing emotions in others | - |  |
| W3C EmotionML + vocabularies | related | <reference role="targetedAt"> | - |  |

### `constellation.narrative_arc` — canonical_open — grounding: **weak**

_The underlying trajectory or story movement represented by the moment_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | related | seven plots / five-stage structure | V |  |
| McAdams narrative identity | related | redemption / contamination; nuclear episodes | K |  |
| Campbell monomyth | related | monomyth stages | - |  |
| Bruner | related | canonicity and breach | K |  |

**`overcoming`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | exact | Overcoming the Monster | V |  |
| McAdams narrative identity | related | redemption sequence | K |  |
| Campbell monomyth | related | The Road of Trials / Ordeal | V |  |
| Lazarus appraisal / coping | related | challenge appraisal | - |  |
| Elliot approach-avoidance | related | approach (mastery) | K |  |

**`transformation`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | exact | Rebirth | V |  |
| McAdams narrative identity | related | redemption; turning point | K |  |
| Campbell monomyth | related | Apotheosis | V |  |
| Pillemer momentous events | related | turning point | - |  |

**`connection`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | exact | communion | K |  |
| Booker seven plots | related | Comedy (ends in union) | V |  |
| Fiske relational models | related | communal sharing | V |  |
| Panksepp primary systems | related | CARE | V |  |

**`reflection`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | meaning-making; exploratory narrative processing | K |  |
| Singer & Blagov SDM | related | integrative memory | - |  |
| Bruner | related | landscape of consciousness | K |  |

**`closure`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | coherent positive resolution | K |  |
| Booker seven plots | related | resolution stage (5-stage structure) | - |  |
| Campbell monomyth | related | Return | V |  |

**`loss`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | exact | Tragedy | V |  |
| McAdams narrative identity | related | contamination sequence; low point | K |  |
| Lazarus appraisal / coping | related | harm/loss appraisal | - |  |
| Singer & Blagov SDM | related | life-threatening events | K |  |
| Panksepp primary systems | related | PANIC/GRIEF | V |  |

**`confrontation`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | related | Overcoming the Monster (nightmare stage) | V |  |
| Campbell monomyth | related | The Road of Trials | V |  |
| McAdams narrative identity | related | agency | K |  |
| Lazarus appraisal / coping | related | confrontive coping | V |  |

### `constellation.relational_dynamics` — canonical_open — grounding: **weak**

_The dominant relational configuration influencing the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | four relational models | - |  |
| Bronfenbrenner ecological systems | related | microsystem relationships | - |  |
| Ainsworth / Main attachment | related | attachment relationships | - |  |
| Singer & Blagov SDM | related | content: relationship | K |  |
| McAdams narrative identity | related | communion | K |  |

**`parent_child`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | related | infant-caregiver attachment | - |  |
| Fiske relational models | related | authority ranking + communal sharing | - |  |
| Bronfenbrenner ecological systems | related | microsystem (family) | K |  |
| McAdams narrative identity | related | communion | K |  |
| Singer & Blagov SDM | related | relationship (content) | - |  |

**`grandparent_grandchild`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | microsystem (family) | K |  |
| Fiske relational models | related | communal sharing | V |  |
| McAdams narrative identity | related | generativity | K |  |

**`romantic_partnership`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | communal sharing | V |  |
| Bartholomew adult attachment | related | adult romantic attachment | - |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000050 passionate love; MFOEM:000049 companionate love | V |  |
| Panksepp primary systems | related | LUST; CARE | V |  |

**`couple`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | communal sharing | V |  |
| Bartholomew adult attachment | related | adult romantic attachment | - |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000049 companionate love | V | duplicate of romantic_partnership |

**`sibling_bond`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | equality matching / communal sharing | V |  |
| Bronfenbrenner ecological systems | related | microsystem (family) | K |  |

**`family`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | exact | microsystem: family | K |  |
| Fiske relational models | related | communal sharing | V |  |

**`friendship`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | equality matching / communal sharing | V |  |
| Bronfenbrenner ecological systems | related | microsystem (peers) | K |  |
| McAdams narrative identity | related | communion | K |  |

**`friend`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | equality matching / communal sharing | V | duplicate of friendship |
| Bronfenbrenner ecological systems | related | microsystem (peers) | K |  |

**`companionship`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | MFOEM:000049 companionate love | V |  |
| Fiske relational models | related | communal sharing | V |  |

**`colleague`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | market pricing / authority ranking | V |  |
| Bronfenbrenner ecological systems | related | microsystem (workplace) | K |  |

**`mentorship`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | authority ranking | V |  |
| Campbell monomyth | related | Supernatural Aid (mentor figure) | V |  |
| McAdams narrative identity | related | generativity | K |  |

**`reunion`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | related | Voyage and Return | V |  |
| Campbell monomyth | related | The Return | V |  |
| Panksepp primary systems | related | PANIC/GRIEF (reunion relief) | V |  |

**`community_ritual`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | mesosystem / macrosystem | K |  |
| Fiske relational models | related | communal sharing | V |  |

**`grief`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | MFOEM:000016 grief | V | an emotion, not a relational configuration |
| Panksepp primary systems | related | PANIC/GRIEF | V |  |
| Lazarus appraisal / coping | related | sadness: irrevocable loss | V |  |
| Singer & Blagov SDM | related | life-threatening events | K |  |

**`self_reflection`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | exploratory narrative processing | K |  |
| Bruner | related | landscape of consciousness | K |  |
| Singer & Blagov SDM | related | integrative memory | - |  |

**`professional`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | market pricing | V |  |
| Bronfenbrenner ecological systems | related | microsystem (workplace) / exosystem | K |  |

**`therapeutic`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | authority ranking / communal sharing | V |  |
| Ainsworth / Main attachment | related | secure base | - |  |

**`service`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | communal sharing / market pricing | V |  |
| McAdams narrative identity | related | generativity script | K |  |

**`adversarial`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Fiske relational models | related | relational-model violation / conflict | - |  |
| Lazarus appraisal / coping | related | anger (demeaning offense) | V |  |
| McAdams narrative identity | related | agency | K |  |
| Panksepp primary systems | related | RAGE | V |  |

### `constellation.temporal_context` — closed_enum — grounding: **weak**

_The life-stage or temporal frame associated with the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | lifetime periods | K | Conway periods are thematic, not age-banded |
| McAdams narrative identity | related | life-story chapters | - |  |
| Bronfenbrenner ecological systems | related | chronosystem | K |  |
| Tulving episodic memory | related | chronesthesia | K |  |

**`childhood`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | lifetime period | - | thematic, not age-banded |
| McAdams narrative identity | related | life-story chapter | - |  |
| Bronfenbrenner ecological systems | related | chronosystem | K |  |

**`early_adulthood`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | lifetime period | - |  |
| McAdams narrative identity | related | life-story chapter | - |  |

**`midlife`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | lifetime period | - |  |
| McAdams narrative identity | related | life-story chapter; generativity | K |  |

**`late_life`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | lifetime period | - |  |
| McAdams narrative identity | related | life-story chapter | - |  |

**`recent`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | recent period / event-specific knowledge | K |  |

**`future`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | exact | episodic future thinking (mental time travel) | - |  |
| McAdams narrative identity | related | generativity script | K |  |

**`timeless`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | related | semantic / noetic | K |  |
| Conway self-memory system | related | general event (repeated) | - |  |

### `constellation.memory_type` — closed_enum — grounding: **weak**

_The class of memory the experience represents within personal identity_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | lifetime period / general event / event-specific knowledge; self-defining memory | K |  |
| Singer & Blagov SDM | related | self-defining memory; specificity | K |  |
| Pillemer momentous events | related | originating / turning-point / anchoring / analogous events | K |  |
| Tulving episodic memory | related | episodic vs semantic | - |  |

**`legacy_artifact`** — grounding: orphan

_orphan_

**`fleeting_moment`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | event-specific knowledge | K |  |
| Tulving episodic memory | related | episodic memory | K |  |
| Singer & Blagov SDM | related | specific memory | - |  |

**`milestone`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Pillemer momentous events | related | turning point; anchoring event | - |  |
| McAdams narrative identity | related | nuclear episode (high point / low point / turning point) | - |  |
| Conway self-memory system | related | general event boundary | - |  |

**`reflection`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Singer & Blagov SDM | related | integrative memory | - |  |
| McAdams narrative identity | related | meaning-making | - |  |

**`formative_experience`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Pillemer momentous events | exact | originating event | - |  |
| Singer & Blagov SDM | related | self-defining memory | K |  |
| Conway self-memory system | related | self-defining memory | - |  |
| McAdams narrative identity | related | nuclear episode | - |  |

### `constellation.media_format` — closed_enum — grounding: **weak**

_The format through which the experience is captured or expressed_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference uri=...> to media | - |  |

**`photo`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference uri> (media) | - |  |

**`video`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference uri> (media) | - |  |

**`audio`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference uri> (media) | - |  |

**`text`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference uri> (media) | - |  |

**`photo_with_story`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference uri> (media) | - |  |

### `constellation.narrative_archetype` — closed_enum — grounding: **weak**

_The archetypal identity the subject embodies — which of the 12 canonical identity archetypes the subject expresses, not a structural role or story function (ADR-0030)_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | imagoes (personified idealised self-images) | K | McAdams 1993 imagoes [KNOWLEDGE] |
| Campbell monomyth | related | the Hero | - |  |

**`hero`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Campbell monomyth | exact | the Hero | - |  |
| McAdams narrative identity | related | imago: Warrior [KNOWLEDGE] | - |  |

**`caregiver`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | imago: Caregiver [KNOWLEDGE] | - |  |
| Panksepp primary systems | related | CARE | V |  |

**`seeker`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Panksepp primary systems | related | SEEKING | V |  |
| Booker seven plots | related | The Quest | V |  |
| McAdams narrative identity | related | imago: Traveler [KNOWLEDGE] | - |  |

**`sage`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | imago: Sage [KNOWLEDGE] | - |  |

**`lover`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | imago: Lover [KNOWLEDGE] | - |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000048 love (disposition) | V |  |

**`outlaw`** — grounding: orphan

_orphan_

**`innocent`** — grounding: orphan

_orphan_

**`magician`** — grounding: orphan

_orphan_

**`creator`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | imago: Maker [KNOWLEDGE] | - |  |

**`everyman`** — grounding: orphan

_orphan_

**`jester`** — grounding: orphan

_orphan_

**`ruler`** — grounding: orphan

_orphan_

### `constellation.symbolic_anchor` — free_text — grounding: **weak**

_A symbolic or material object, place, or element that concentrates meaning_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Pillemer momentous events | related | sensory / symbolic detail of personal event memory | K |  |
| Conway self-memory system | related | event-specific knowledge cue | - |  |
| Tulving episodic memory | related | retrieval cue (encoding specificity) | - |  |
| W3C EmotionML + vocabularies | related | <reference role="targetedAt"> | - |  |

### `constellation.relational_perspective` — closed_enum — grounding: **weak**

_The perspective through which the experience is narrated or understood_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | nested systems (micro -> macro) | - |  |
| McAdams narrative identity | related | agency vs communion | - |  |

**`self`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | agency | K |  |
| Bronfenbrenner ecological systems | related | person (centre of nested systems) | K |  |

**`partner`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | microsystem | K |  |
| McAdams narrative identity | related | communion | K |  |

**`family`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | exact | microsystem: family | K |  |

**`friends`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | exact | microsystem: peers | K |  |

**`community`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | mesosystem / exosystem | K |  |

**`humanity`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | macrosystem | K |  |
| Cowen & Keltner 2017 | related | awe (self-transcendent) | V |  |

### `constellation.temporal_rhythm` — closed_enum — grounding: **weak**

_The perceived temporal movement or cadence of the emotional event_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <trace> (time-varying intensity); start/end/duration attributes | V |  |
| Scherer CPM / GRID / GEW | related | novelty check: suddenness | - |  |
| OBO MFOEM Emotion Ontology | related | appraisal of suddenness (MFOEM:000057) | V |  |

**`still`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <trace> flat | - |  |
| Russell circumplex | related | low arousal | - |  |

**`sudden`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | exact | MFOEM:000062 appraisal as sudden | V |  |
| Scherer CPM / GRID / GEW | exact | suddenness (novelty check) | K |  |
| W3C EmotionML + vocabularies | exact | scherer-appraisals#suddenness | V |  |
| HUMAINE EARL | exact | suddenness (appraisal) | V |  |

**`rising`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <trace> increasing | - |  |

**`fading`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <trace> decreasing | - |  |

**`recurring`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | repeated general event | - |  |
| Pillemer momentous events | related | analogous events | K |  |

**`spiraling`** — grounding: orphan

_orphan_

**`dragging`** — grounding: orphan

_orphan_

**`suspended`** — grounding: orphan

_orphan_

**`looping`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | repeated general event | - | overlaps recurring |

**`cyclic`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | repeated general event | - | overlaps recurring / gravity.recurrence_pattern=cyclical |

### `constellation.identity_thread` — free_text — grounding: **strong**

_A succinct expression of how the experience connects to personal identity_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | exact | self-memory system: memory-self linkage | - |  |
| McAdams narrative identity | exact | narrative identity | K |  |
| Singer & Blagov SDM | related | self-defining memory | K |  |
| Pillemer momentous events | related | self function of autobiographical memory | - |  |
| Tulving episodic memory | related | autonoetic consciousness | - |  |

### `constellation.expressed_insight` — free_text — grounding: **strong**

_The explicit realization or conclusion stated by the subject_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | exact | meaning-making (lesson / insight) | - |  |
| Singer & Blagov SDM | exact | integrative meaning | K |  |
| Pillemer momentous events | related | directive function (lessons) | - |  |
| Gross process model | related | cognitive change (reappraisal) | K |  |

### `constellation.transformational_pivot` — boolean — grounding: **strong**

_Marks experiences the subject explicitly identifies as life-changing or trajectory-altering at time of extraction_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | exact | turning point (nuclear episode) | K |  |
| Pillemer momentous events | exact | turning point | - |  |
| Singer & Blagov SDM | related | self-defining memory | K |  |
| Campbell monomyth | related | crossing of the first threshold | V |  |

### `constellation.somatic_signature` — free_text — grounding: **strong**

_Bodily or interoceptive sensations explicitly described by the subject as part of the emotional experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Damasio | exact | somatic marker / feeling as perception of body state | V |  |
| Barrett constructed emotion | exact | interoception | V |  |
| Scherer CPM / GRID / GEW | exact | bodily reactions component (GRID); physiological component (CPM) | - |  |
| OBO MFOEM Emotion Ontology | exact | physiological process involved in an emotion (MFOEM:000003) | V | subclasses: shivering, heart beating faster, lump in throat, ... |
| Panksepp primary systems | related | primary-process bodily arousal | - |  |
| SNOMED CT | related | symptom / finding codes | - |  |

### `constellation.arc_type` — canonical_open — grounding: **weak**

_The structural emotional arc pattern of the experience, encoded at capture time_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | related | seven plots | V |  |
| Campbell monomyth | related | monomyth stages | - |  |
| McAdams narrative identity | related | redemption / contamination; nuclear episodes | K |  |
| Lazarus appraisal / coping | related | core relational themes | V |  |

**`betrayal`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | anger: demeaning offense | V |  |
| McAdams narrative identity | related | contamination sequence | K |  |
| Booker seven plots | related | Tragedy | V |  |
| Fiske relational models | related | relational-model violation | - |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000225 mistrust | V |  |

**`liberation`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Campbell monomyth | exact | Freedom to Live | V |  |
| Booker seven plots | related | Rebirth | V |  |
| McAdams narrative identity | related | redemption sequence | K |  |
| Self-determination theory | related | autonomy | V |  |

**`grief`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | exact | MFOEM:000016 grief | V |  |
| Panksepp primary systems | exact | PANIC/GRIEF | V |  |
| Lazarus appraisal / coping | exact | sadness: irrevocable loss | V |  |
| Plutchik wheel | exact | grief (high-intensity sadness) | K |  |
| SenticNet Hourglass | exact | grief (Pleasantness level) | V |  |
| McAdams narrative identity | related | contamination; low point | K |  |
| Booker seven plots | related | Tragedy | V |  |

**`discovery`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | related | The Quest; Voyage and Return | V |  |
| Campbell monomyth | related | The Call to Adventure | V |  |
| Cowen & Keltner 2017 | related | interest | V |  |
| Panksepp primary systems | related | SEEKING | V |  |
| McAdams narrative identity | related | exploratory narrative processing | K |  |
| Singer & Blagov SDM | related | recreation / exploration (content) | K |  |

**`resistance`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | agency | K |  |
| Lazarus appraisal / coping | related | confrontive coping | V |  |
| Booker seven plots | related | Overcoming the Monster | V |  |
| Campbell monomyth | related | Refusal of the Call | V |  |

**`bond`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | exact | communion | K |  |
| Ainsworth / Main attachment | related | attachment bond | - |  |
| Fiske relational models | related | communal sharing | V |  |
| Panksepp primary systems | related | CARE | V |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000049 companionate love | V |  |

**`moral_awakening`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | meaning-making; redemption | K |  |
| OCC | related | attribution branch (pride / shame / admiration / reproach) | - |  |
| Lazarus appraisal / coping | related | guilt: moral transgression | V |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000023 moral disgust; MFOEM:000053 guilt | V |  |
| Campbell monomyth | related | Apotheosis | V |  |

**`transformation`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Booker seven plots | exact | Rebirth | V |  |
| McAdams narrative identity | related | redemption sequence | K |  |
| Campbell monomyth | related | Apotheosis; The Ultimate Boon | V |  |
| Pillemer momentous events | related | turning point | - | duplicate of narrative_arc=transformation |

**`reconciliation`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | redemption; communion | K |  |
| Booker seven plots | related | Comedy (resolution via reunion) | V |  |
| Fiske relational models | related | relational-model restoration | - |  |

**`reckoning`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | secondary appraisal: blame / credit (accountability) | V |  |
| OCC | related | reproach / self-reproach (shame, remorse) | K |  |
| McAdams narrative identity | related | contamination; meaning-making | K |  |
| Booker seven plots | related | Tragedy (nightmare stage) | V |  |
| Campbell monomyth | related | Atonement with the Father | V |  |

**`threshold`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Campbell monomyth | exact | The Crossing of the First Threshold | V |  |
| Booker seven plots | related | anticipation -> dream stage | - |  |
| Pillemer momentous events | related | turning point | - |  |
| McAdams narrative identity | related | turning point | K |  |

**`exile`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Campbell monomyth | related | Belly of the Whale; Departure | V |  |
| Booker seven plots | related | Voyage and Return; Tragedy | V |  |
| McAdams narrative identity | related | contamination | K |  |
| Panksepp primary systems | related | PANIC/GRIEF (separation distress) | V |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000227 loneliness | V |  |

**`gratitude`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| GoEmotions | exact | gratitude | V | duplicate of emotion_primary=gratitude |
| OCC | exact | gratitude | K |  |
| W3C EmotionML + vocabularies | exact | occ-categories#gratitude | V |  |
| WordNet-Affect | exact | gratitude | - |  |
| Lazarus appraisal / coping | exact | gratitude | - |  |
| McAdams narrative identity | related | redemption | K |  |

**`authenticity`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Self-determination theory | related | autonomy (self-endorsement); integrated regulation | V |  |
| McAdams narrative identity | related | identity integration / coherence | - |  |
| Bar-On EQ-i | related | self-regard; self-actualization | V | duplicate of motivational_orientation=authenticity |

## MILKY_WAY


### `milky_way.event_type` — free_text — grounding: **weak**

_Type of event or situation_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Singer & Blagov SDM | related | content category | K |  |
| OCC | related | consequences of events branch | - |  |
| Pillemer momentous events | related | personal event memory types | - |  |
| Conway self-memory system | related | general events | K |  |
| W3C EmotionML + vocabularies | related | <reference role="triggeredBy"> | - |  |
| Lazarus appraisal / coping | related | encounter | - |  |

### `milky_way.location_context` — free_text — grounding: **weak**

_Place or spatial context of the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | microsystem setting | - |  |
| Tulving episodic memory | related | spatial context of episodic memory | - |  |
| Conway self-memory system | related | event-specific knowledge | K |  |
| Pillemer momentous events | related | specific location detail | - |  |

### `milky_way.associated_people` — free_text_list — grounding: **weak**

_Individuals referenced in or connected to the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | microsystem members | - |  |
| W3C EmotionML + vocabularies | related | <reference role="targetedAt" | "expressedBy"> | - |  |
| Fiske relational models | related | relational partners | - |  |
| Singer & Blagov SDM | related | content: relationship | K |  |

### `milky_way.visibility_context` — closed_enum — grounding: **orphan**

_Defines the intended visibility or sharing scope of the moment_

_No framework mapping (orphan)._

**`private`** — grounding: orphan

_orphan_

**`family_only`** — grounding: orphan

_orphan_

**`shared_publicly`** — grounding: orphan

_orphan_

### `milky_way.tone_shift` — free_text — grounding: **strong**

_Directional emotional change during the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | exact | redemption (bad->good) / contamination (good->bad) sequence | K | EDM is finer (any pair); McAdams has two directions |
| W3C EmotionML + vocabularies | related | <trace>; sequence of timed <emotion> elements | V |  |
| Russell circumplex | related | trajectory in affect space | - |  |
| Scherer CPM / GRID / GEW | related | recursive appraisal -> emotion change | - |  |
| Lazarus appraisal / coping | related | reappraisal | V |  |
| Gross process model | related | regulation outcome | - |  |

## GRAVITY


### `gravity.emotional_weight` — numeric — grounding: **strong**

_The felt intensity of the emotional experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | exact | <dimension name="intensity"> from intensity-dimension vocabulary (0..1) | - | intensity is a dimension, not an element, in EmotionML 1.0 |
| HUMAINE EARL | exact | intensity attribute | - |  |
| Plutchik wheel | exact | intensity axis (3 levels) | - | EDM continuous is finer |
| NRC lexicons | exact | NRC Emotion Intensity Lexicon (0..1) | V |  |
| Singer & Blagov SDM | exact | SDM criterion: affective intensity | - |  |
| Conway self-memory system | exact | SDM criterion: affective intensity | - |  |
| Scherer CPM / GRID / GEW | related | intensity (CPM emergent) | - |  |
| Russell circumplex | related | arousal | K |  |
| PAD (Mehrabian & Russell) | related | Arousal | K |  |
| Barrett constructed emotion | related | core affect arousal | - |  |
| SenticNet Hourglass | related | sentic level magnitude | - |  |
| Hume semantic space | related | expression score 0..1 | - |  |
| Pillemer momentous events | related | emotional arousal at encoding -> vividness | - |  |

### `gravity.emotional_density` — closed_enum — grounding: **weak**

_How concentrated or layered the emotional content is_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | related | dyads (mixed emotions) | K |  |
| Cowen & Keltner 2017 | related | blends | - |  |
| Barrett constructed emotion | related | emotional granularity | K | granularity is a person-level trait, not an event property |
| W3C EmotionML + vocabularies | related | multiple <category> elements | - |  |

**`low`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Barrett constructed emotion | related | low granularity / single category | - |  |

**`medium`** — grounding: orphan

_orphan_

**`high`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | related | dyad (mixed) | - |  |
| Cowen & Keltner 2017 | related | blend | - |  |

### `gravity.valence` — closed_enum — grounding: **strong**

_The qualitative direction of the emotional experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Russell circumplex | exact | pleasure-displeasure dimension | - |  |
| PAD (Mehrabian & Russell) | exact | Pleasure | K |  |
| Scherer CPM / GRID / GEW | exact | GRID valence dimension | - |  |
| Barrett constructed emotion | exact | core affect valence | - |  |
| OBO MFOEM Emotion Ontology | exact | valence (MFOEM:000194): positive valence (MFOEM:000207) / negative valence (MFOEM:000208) | V | MFOEM has no "mixed" |
| W3C EmotionML + vocabularies | exact | pad-dimensions#pleasure; fsre-dimensions#valence | V |  |
| HUMAINE EARL | exact | valence (dimension) | V |  |
| NRC lexicons | exact | NRC VAD valence; EmoLex positive/negative | V |  |
| SenticNet Hourglass | exact | polarity | V |  |
| WordNet-Affect | exact | positive / negative / ambiguous / neutral | V | "ambiguous" = EDM mixed |
| GoEmotions | exact | sentiment grouping: positive / negative / ambiguous / neutral | V |  |
| Singer & Blagov SDM | exact | affect: positive / negative / mixed / neutral | K |  |
| OCC | exact | pleased / displeased root | K |  |
| Lazarus appraisal / coping | related | goal congruence / incongruence | V |  |
| McAdams narrative identity | related | redemption / contamination valence | K |  |
| Plutchik wheel | related | opposition pairs | V |  |
| Hume semantic space | related | valence (dimension view) | - |  |
| Cowen & Keltner 2017 | related | valence (appraisal dimension) | - |  |

**`positive`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | exact | MFOEM:000207 positive valence | V |  |
| WordNet-Affect | exact | positive | V |  |
| GoEmotions | exact | positive | V |  |
| Singer & Blagov SDM | exact | positive | K |  |
| NRC lexicons | exact | positive (EmoLex) | V |  |
| OCC | exact | pleased | K |  |
| Russell circumplex | exact | pleasure pole | - |  |
| PAD (Mehrabian & Russell) | exact | +P | - |  |
| SenticNet Hourglass | exact | positive polarity | - |  |

**`negative`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | exact | MFOEM:000208 negative valence | V |  |
| WordNet-Affect | exact | negative | V |  |
| GoEmotions | exact | negative | V |  |
| Singer & Blagov SDM | exact | negative | K |  |
| NRC lexicons | exact | negative (EmoLex) | V |  |
| OCC | exact | displeased | K |  |
| Russell circumplex | exact | displeasure pole | - |  |
| PAD (Mehrabian & Russell) | exact | -P | - |  |
| SenticNet Hourglass | exact | negative polarity | - |  |

**`mixed`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| WordNet-Affect | exact | ambiguous | V |  |
| GoEmotions | exact | ambiguous | V |  |
| Singer & Blagov SDM | exact | mixed | K |  |
| Plutchik wheel | related | dyad | - |  |
| OBO MFOEM Emotion Ontology | related | no class (positive + negative valence co-instantiated) | - |  |

### `gravity.viscosity` — closed_enum — grounding: **weak**

_The perceived "stickiness" or persistence of the emotion_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Scherer CPM / GRID / GEW | related | duration; emotion vs mood | - |  |
| OBO MFOEM Emotion Ontology | related | mood process (MFOEM:000193) vs emotion process | - |  |
| W3C EmotionML + vocabularies | related | duration attribute | - |  |
| Damasio | related | background emotions | K |  |

**`low`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | emotion process (short) | V |  |

**`medium`** — grounding: orphan

_orphan_

**`high`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | mood process (MFOEM:000193) | V |  |

**`enduring`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | mood process; emotion disposition (MFOEM:000199) | V |  |
| Damasio | related | background emotion | - |  |

**`fluid`** — grounding: orphan

_orphan_

### `gravity.gravity_type` — free_text — grounding: **weak**

_Category or nature of the emotional pull_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | types of ego-involvement (self/social esteem, moral values, ego-ideals, meanings, others, life goals) | - |  |
| Conway self-memory system | related | self-relevance | - |  |
| Pillemer momentous events | related | personal significance | - |  |

### `gravity.tether_type` — canonical_open — grounding: **weak**

_The type of element to which the experience is emotionally anchored_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | related | <reference role="targetedAt"> (any URI) | - |  |
| OCC | related | events / agents / objects branches | K |  |
| Conway self-memory system | related | working self; autobiographical knowledge base | V |  |
| Lazarus appraisal / coping | related | object of ego-involvement | - |  |
| Tulving episodic memory | related | cue type | - |  |
| Bronfenbrenner ecological systems | related | setting | - |  |

**`person`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OCC | exact | agents branch | - |  |
| W3C EmotionML + vocabularies | related | <reference role="targetedAt"> | - |  |
| Fiske relational models | related | relational partner | - |  |

**`symbol`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OCC | related | objects branch | - |  |
| Pillemer momentous events | related | symbolic detail | - |  |

**`event`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OCC | exact | events branch | - |  |
| Conway self-memory system | related | general event / ESK | K |  |
| Pillemer momentous events | related | personal event memory | K |  |

**`place`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | microsystem setting | - |  |
| Tulving episodic memory | related | spatial context | - |  |

**`ritual`** — grounding: orphan

_orphan_

**`object`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OCC | exact | objects branch | - |  |
| Pillemer momentous events | related | sensory / object detail | K |  |

**`tradition`** — grounding: orphan

_orphan_

**`identity`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | working self | V |  |
| McAdams narrative identity | related | narrative identity | K |  |
| Lazarus appraisal / coping | related | ego-involvement | V |  |

**`self`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | working self | V |  |
| McAdams narrative identity | related | agency | K |  |

### `gravity.recall_triggers` — free_text_list — grounding: **strong**

_Sensory or symbolic cues that reactivate the memory_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | exact | retrieval cue (encoding specificity principle) | - |  |
| Conway self-memory system | exact | sensory-perceptual cue -> direct retrieval | - |  |
| Pillemer momentous events | exact | sensory imagery cue | - |  |
| Damasio | related | somatic marker as cue | - |  |

### `gravity.retrieval_keys` — free_text_list — grounding: **strong**

_Compact hooks for memory retrieval_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | exact | retrieval cue | - |  |
| Conway self-memory system | related | generative retrieval index | - |  |

### `gravity.nearby_themes` — free_text_list — grounding: **weak**

_Adjacent themes or motifs connected to the experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | thematic linkage of general events | - |  |
| McAdams narrative identity | related | agency / communion themes | K |  |
| Singer & Blagov SDM | related | content categories | - |  |

### `gravity.recurrence_pattern` — canonical_open — grounding: **weak**

_The temporal recurrence structure extracted from the experience's context, framing, and temporal markers_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | single vs repeated general events | - |  |
| Singer & Blagov SDM | related | specificity: specific vs generic (summary of repeated events) | K |  |
| Pillemer momentous events | related | anchoring / analogous events | K |  |
| Lazarus appraisal / coping | related | chronic stressor | - |  |

**`cyclical`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | repeated general event | - |  |
| Singer & Blagov SDM | related | generic / summary memory | K |  |

**`isolated`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | single event | - |  |
| Singer & Blagov SDM | related | specific memory | - |  |
| Pillemer momentous events | related | personal event memory (single) | K |  |

**`chronic`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | chronic stressor | - |  |
| Conway self-memory system | related | extended event / lifetime period | - |  |

**`emerging`** — grounding: orphan

_orphan_

### `gravity.strength_score` — numeric — grounding: **weak**

_The binding strength of the emotion within the broader emotional network_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Conway self-memory system | related | SDM criterion: linkage to similar memories | - |  |
| Singer & Blagov SDM | related | SDM criterion: linked to other similar memories | - |  |

### `gravity.temporal_decay` — closed_enum — grounding: **weak**

_How quickly the emotional intensity is expected to diminish over time_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Scherer CPM / GRID / GEW | related | duration | - |  |
| W3C EmotionML + vocabularies | related | duration attribute | - |  |
| Pillemer momentous events | related | persistence of vividness | - |  |
| Conway self-memory system | related | retention | - |  |

**`fast`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Scherer CPM / GRID / GEW | related | short duration | - |  |

**`moderate`** — grounding: orphan

_orphan_

**`slow`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | mood process | V |  |

### `gravity.resilience_markers` — free_text_list — grounding: **weak**

_Indicators of stabilizing or constructive emotional processing_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | positive reappraisal; emotion-focused coping | V |  |
| Gross process model | related | cognitive change | K |  |
| McAdams narrative identity | related | redemption; coherent positive resolution | K |  |
| Bar-On EQ-i | related | stress tolerance; optimism; adaptability | V |  |
| Goleman EI | related | positive outlook; adaptability | V |  |

### `gravity.adaptation_trajectory` — closed_enum — grounding: **weak**

_How the emotional state is evolving across time_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | redemption (improving) / contamination (declining) / coherent positive resolution (integrative) | K |  |
| Singer & Blagov SDM | related | integrative vs non-integrative | - |  |
| Gross process model | related | regulation outcome over time | - |  |
| Lazarus appraisal / coping | related | coping outcome | - |  |

**`improving`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | redemption sequence | K |  |

**`stable`** — grounding: orphan

_orphan_

**`declining`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | contamination sequence | K |  |

**`integrative`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Singer & Blagov SDM | exact | integrative | K |  |
| McAdams narrative identity | related | coherent positive resolution | K |  |

**`emerging`** — grounding: orphan

_orphan_

## IMPULSE


### `impulse.primary_energy` — free_text — grounding: **weak**

_Dominant emotional or motivational energy in the moment_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Panksepp primary systems | related | primary-process emotional systems | V |  |
| Elliot approach-avoidance | related | approach / avoidance temperament | K |  |
| Self-determination theory | related | intrinsic motivation | K |  |
| OBO MFOEM Emotion Ontology | related | feeling of urge (MFOEM:000223); feeling of desire (MFOEM:000220) | V |  |
| W3C EmotionML + vocabularies | related | <action-tendency> | V |  |

### `impulse.drive_state` — closed_enum — grounding: **strong**

_The behavioral direction or movement expressed through the emotional response_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| W3C EmotionML + vocabularies | exact | <action-tendency name= set=frijda-action-tendencies> | - |  |
| OBO MFOEM Emotion Ontology | exact | emotional action tendency (MFOEM:000007); emotional bodily movement behaviour | V |  |
| Elliot approach-avoidance | related | approach / avoidance | K |  |
| Plutchik wheel | related | 8 adaptive behaviours (protection, destruction, incorporation, rejection, reproduction, reintegration, orientation, exploration) | - |  |
| Panksepp primary systems | related | primary systems (SEEKING, RAGE, FEAR, CARE, ...) | - |  |
| Lazarus appraisal / coping | related | Ways of Coping | V |  |
| Gross process model | related | situation selection / modification | K |  |

**`explore`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | exact | exploration (adaptive behaviour of anticipation) | - |  |
| Panksepp primary systems | exact | SEEKING | V |  |
| W3C EmotionML + vocabularies | related | frijda-action-tendencies#attending | V |  |
| Cowen & Keltner 2017 | related | interest | V |  |

**`approach`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Elliot approach-avoidance | exact | approach | K |  |
| W3C EmotionML + vocabularies | exact | frijda-action-tendencies#approach | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000136 moving towards people | V |  |
| Plutchik wheel | related | incorporation | - |  |

**`avoid`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Elliot approach-avoidance | exact | avoidance | K |  |
| W3C EmotionML + vocabularies | exact | frijda-action-tendencies#avoidance | V |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000137 moving away from people | V |  |
| Plutchik wheel | related | protection (fear) | - |  |
| Lazarus appraisal / coping | related | escape-avoidance | V |  |

**`repair`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | planful problem-solving; positive reappraisal | V |  |
| Gross process model | related | situation modification | K |  |
| McAdams narrative identity | related | redemption | K |  |

**`persevere`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Elliot approach-avoidance | related | mastery-approach | K |  |
| Lazarus appraisal / coping | related | planful problem-solving | - |  |
| Self-determination theory | related | competence | V |  |

**`share`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | seeking social support | V |  |
| W3C EmotionML + vocabularies | related | frijda-action-tendencies#being-with | V |  |
| McAdams narrative identity | related | communion | K |  |

**`confront`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | confrontive coping | V |  |
| W3C EmotionML + vocabularies | related | frijda-action-tendencies#agonistic | V |  |
| Panksepp primary systems | related | RAGE | V |  |
| Plutchik wheel | related | destruction (anger) | - |  |

**`protect`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Plutchik wheel | exact | protection (adaptive behaviour of fear) | - |  |
| Panksepp primary systems | related | CARE; FEAR | V |  |
| W3C EmotionML + vocabularies | related | frijda-action-tendencies#dominating | V |  |

**`process`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Gross process model | related | cognitive change | K |  |
| Singer & Blagov SDM | related | integrative meaning | K |  |

### `impulse.motivational_orientation` — closed_enum — grounding: **strong**

_The foundational motivational domain guiding the individual's internal stance_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Self-determination theory | exact | basic psychological needs (autonomy, competence, relatedness) | V | EDM adds safety, meaning, authenticity |
| Elliot approach-avoidance | related | mastery goals | - |  |
| Panksepp primary systems | related | SEEKING / CARE / PANIC / FEAR | V |  |
| McAdams narrative identity | related | agency / communion / generativity | K |  |
| Bar-On EQ-i | related | self-actualization | V |  |

**`belonging`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Self-determination theory | exact | relatedness | V |  |
| Panksepp primary systems | related | CARE; PANIC/GRIEF | V |  |
| McAdams narrative identity | related | communion | K |  |
| Ainsworth / Main attachment | related | attachment | V |  |

**`safety`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | related | felt security / secure base | - |  |
| Lazarus appraisal / coping | related | threat appraisal | - |  |
| Panksepp primary systems | related | FEAR | V |  |

**`mastery`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Self-determination theory | exact | competence | V |  |
| Elliot approach-avoidance | exact | mastery-approach goal | - |  |
| McAdams narrative identity | related | agency | K |  |

**`meaning`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | meaning-making; generativity | K |  |
| Bar-On EQ-i | related | self-actualization | V |  |
| Singer & Blagov SDM | related | integrative meaning | K |  |

**`autonomy`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Self-determination theory | exact | autonomy | V |  |
| McAdams narrative identity | related | agency | K |  |

**`authenticity`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Self-determination theory | related | autonomy (self-endorsement); integrated regulation | V |  |
| Bar-On EQ-i | related | self-regard | V |  |

### `impulse.temporal_focus` — closed_enum — grounding: **strong**

_The temporal direction toward which the motivational energy is oriented_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | exact | chronesthesia / mental time travel (past, future) | K |  |
| Conway self-memory system | related | working self goals | - |  |
| McAdams narrative identity | related | life story (past) / generativity script (future) | K |  |

**`past`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | exact | episodic retrieval (mental time travel: past) | - |  |
| McAdams narrative identity | related | life story | K |  |

**`present`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | related | noetic awareness | - |  |

**`future`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Tulving episodic memory | exact | episodic future thinking | - |  |
| McAdams narrative identity | related | generativity script | K |  |
| Self-determination theory | related | goal pursuit | - |  |

### `impulse.directionality` — closed_enum — grounding: **weak**

_Whether the impulse is self-directed, relational, or expansive beyond self_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | agency (self) / communion (other) | K |  |
| Bronfenbrenner ecological systems | related | nested systems | - |  |
| Cowen & Keltner 2017 | related | awe (self-transcendent) | V |  |

**`inward`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | agency | K |  |
| Gross process model | related | intrinsic regulation | - |  |

**`outward`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | related | communion | K |  |
| Gross process model | related | extrinsic (interpersonal) regulation | - |  |

**`transcendent`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Cowen & Keltner 2017 | related | awe | V |  |
| Bronfenbrenner ecological systems | related | macrosystem | K |  |

### `impulse.social_visibility` — closed_enum — grounding: **weak**

_The social scope within which the impulse is expressed_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | micro / meso systems | - |  |

**`private`** — grounding: orphan

_orphan_

**`relational`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | microsystem | K |  |

**`collective`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Bronfenbrenner ecological systems | related | mesosystem / macrosystem | K |  |

### `impulse.urgency` — closed_enum — grounding: **strong**

_The intensity or immediacy of the motivational state_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Scherer CPM / GRID / GEW | exact | urgency check (implication SEC) | - |  |
| W3C EmotionML + vocabularies | exact | ema-appraisals#urgency; scherer-appraisals#urgency | V |  |
| HUMAINE EARL | exact | goal_urgency (appraisal) | V |  |
| OBO MFOEM Emotion Ontology | exact | appraisal of urgency of response (MFOEM:000088): urgent (MFOEM:000089) / not urgent (MFOEM:000090) | V | EDM 4 levels finer than MFOEM binary |
| Russell circumplex | related | arousal | K |  |
| PAD (Mehrabian & Russell) | related | Arousal | K |  |
| NRC lexicons | related | VAD arousal | - |  |
| Lazarus appraisal / coping | related | imminence | - |  |

**`calm`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | exact | MFOEM:000090 appraisal as not urgent response | V |  |
| Russell circumplex | related | calm (low arousal) | K | label collides with emotion peace |

**`elevated`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Russell circumplex | related | mid arousal | - |  |

**`pressing`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | MFOEM:000089 appraisal as urgent response | V |  |

**`acute`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | exact | MFOEM:000089 appraisal as urgent response | V |  |
| Russell circumplex | related | high arousal | - |  |

### `impulse.risk_posture` — closed_enum — grounding: **weak**

_The stance toward uncertainty or potential risk embedded in the moment_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | threat vs challenge appraisal | - |  |
| Elliot approach-avoidance | related | approach vs avoidance temperament | - |  |
| OBO MFOEM Emotion Ontology | related | appraisal of dangerousness (MFOEM:000103) | V |  |
| Bar-On EQ-i | related | impulse control; reality testing | V |  |
| Panksepp primary systems | related | FEAR / SEEKING balance | V |  |

**`cautious`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | threat appraisal | - |  |
| Elliot approach-avoidance | related | avoidance temperament | K |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000104 appraisal as dangerous | V |  |

**`balanced`** — grounding: orphan

_orphan_

**`bold`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | challenge appraisal | - |  |
| Elliot approach-avoidance | related | approach temperament | K |  |
| OBO MFOEM Emotion Ontology | related | MFOEM:000105 appraisal as not dangerous | V |  |

### `impulse.agency_level` — closed_enum — grounding: **strong**

_The perceived ability to act or influence the situation_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| McAdams narrative identity | exact | agency theme | - |  |
| Scherer CPM / GRID / GEW | exact | coping potential (control / power checks); GRID power dimension | K |  |
| Lazarus appraisal / coping | exact | secondary appraisal: coping potential | V |  |
| PAD (Mehrabian & Russell) | exact | Dominance | K |  |
| NRC lexicons | exact | VAD dominance | - |  |
| W3C EmotionML + vocabularies | exact | pad-dimensions#dominance; fsre-dimensions#potency; ema-appraisals#controllability; scherer-appraisals#control; scherer-appraisals#power | V |  |
| HUMAINE EARL | exact | power (dimension); event_controllability; agent_power (appraisals) | V |  |
| OBO MFOEM Emotion Ontology | related | feeling in control (MFOEM:000110) / feeling out of control (MFOEM:000116) | V |  |
| Self-determination theory | related | autonomy; competence | V |  |
| Bruner | related | agentivity (intentional state entailment) | - |  |

**`low`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| PAD (Mehrabian & Russell) | exact | -D | - |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000116 feeling out of control | V |  |
| Scherer CPM / GRID / GEW | exact | low coping potential / power | K |  |

**`medium`** — grounding: orphan

_orphan_

**`high`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| PAD (Mehrabian & Russell) | exact | +D | - |  |
| OBO MFOEM Emotion Ontology | exact | MFOEM:000110 feeling in control | V |  |
| Scherer CPM / GRID / GEW | exact | high coping potential / power | K |  |

### `impulse.regulation_state` — closed_enum — grounding: **moderate**

_The stability or turbulence of emotional self-regulation_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Gross process model | broader | emotion regulation (process model) | K | Gross names strategies, not state levels |
| Mayer-Salovey EI | related | branch 4: managing emotions | - |  |
| Goleman EI | related | emotional self-control | V |  |
| Bar-On EQ-i | related | impulse control; stress tolerance | V |  |
| OBO MFOEM Emotion Ontology | related | feeling in control / feeling out of control | V |  |
| SNOMED CT | related | emotional lability / dysregulation findings | - | see frameworks.json |

**`regulated`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | MFOEM:000110 feeling in control | V |  |
| Goleman EI | related | emotional self-control | V |  |

**`wavering`** — grounding: orphan

_orphan_

**`dysregulated`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| OBO MFOEM Emotion Ontology | related | MFOEM:000116 feeling out of control | V |  |
| SNOMED CT | related | emotional lability (see frameworks.json) | - |  |

### `impulse.attachment_style` — closed_enum — grounding: **strong**

_The relational attachment pattern influencing the emotional expression_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | exact | Strange Situation A/B/C + Main & Solomon D | - |  |
| Bartholomew adult attachment | related | secure / preoccupied / dismissing / fearful | K | different partition |
| Panksepp primary systems | related | CARE / PANIC-GRIEF | V |  |

**`secure`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | exact | B: secure | - |  |
| Bartholomew adult attachment | exact | secure | K |  |
| Ainsworth / Main attachment | exact | Hazan & Shaver: secure | - |  |

**`anxious`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | exact | C: anxious-ambivalent / resistant | V |  |
| Bartholomew adult attachment | related | preoccupied | K |  |

**`avoidant`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | exact | A: avoidant | - |  |
| Bartholomew adult attachment | related | dismissing | K |  |

**`disorganized`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Ainsworth / Main attachment | exact | D: disorganized / disoriented (Main & Solomon) | K |  |
| Bartholomew adult attachment | related | fearful | K | contested equivalence |

### `impulse.coping_style` — canonical_open — grounding: **strong**

_The primary strategy used to manage or integrate the emotional experience_

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | Ways of Coping (8 scales) | V |  |
| Gross process model | exact | emotion regulation strategy families | - |  |
| Mayer-Salovey EI | related | managing emotions | K |  |
| Bar-On EQ-i | related | stress management composite | - |  |
| Goleman EI | related | self-management | - |  |

**`reframe_meaning`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | positive reappraisal | V |  |
| Gross process model | exact | cognitive change (reappraisal) | K |  |
| McAdams narrative identity | related | redemption / meaning-making | K |  |

**`seek_support`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | seeking social support | V |  |
| Gross process model | related | situation selection (interpersonal regulation) | K |  |

**`distract`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Gross process model | exact | attentional deployment (distraction) | K |  |
| Lazarus appraisal / coping | related | escape-avoidance | V |  |

**`ritualize`** — grounding: orphan

_orphan_

**`confront`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | confrontive coping | V |  |
| Gross process model | related | situation modification | K |  |

**`detach`** — grounding: strong

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | exact | distancing | V |  |
| Gross process model | related | response modulation (suppression) | K |  |

**`process`** — grounding: weak

| Framework | Relation | Target | Ver. | Note |
|---|---|---|---|---|
| Lazarus appraisal / coping | related | emotion-focused coping | K |  |
| Gross process model | related | cognitive change | K |  |
| Singer & Blagov SDM | related | integrative meaning | K |  |


## Gap list A — Orphans (EDM rows with no mapping anywhere)

| Row | Decision | Reason |
|---|---|---|
| `constellation.memory_type=legacy_artifact` | merge | Object-mediated memory (material culture, "evocative objects") is not a memory *type* in Conway / Singer & Blagov / Pillemer; it is a tether. Covered by gravity.tether_type=object (and =tradition). Cut from memory_type. |
| `constellation.narrative_archetype=outlaw` | cut | The 12-archetype set is Mark & Pearson (2001) brand archetypes [KNOWLEDGE], not a memory/significance construct. Nearest academic construct is McAdams imagoes (1993), which uses a different, open list. Move the whole field to EXTENSIONS or replace with a McAdams imago code. |
| `constellation.narrative_archetype=innocent` | cut | see outlaw |
| `constellation.narrative_archetype=magician` | cut | see outlaw |
| `constellation.narrative_archetype=everyman` | cut | see outlaw |
| `constellation.narrative_archetype=jester` | cut | see outlaw |
| `constellation.narrative_archetype=ruler` | cut | see outlaw |
| `constellation.temporal_rhythm=spiraling` | keep | Phenomenological time of affect (Fuchs 2013 "Temporality and psychopathology"; Minkowski) [KNOWLEDGE] is not in the listed frameworks; the nearest machine home is an EmotionML <trace>, which cannot express shape qualities such as spiralling. Keep as EDM-specific; candidate for the ontology experiment. |
| `constellation.temporal_rhythm=dragging` | keep | see spiraling |
| `constellation.temporal_rhythm=suspended` | keep | see spiraling |
| `milky_way.visibility_context` | cut | Non-affective sharing scope; duplicates meta.visibility (governance). No affective framework models it because it is a data-governance property, not a property of the experience. |
| `milky_way.visibility_context=private` | cut | see field |
| `milky_way.visibility_context=family_only` | cut | see field |
| `milky_way.visibility_context=shared_publicly` | cut | see field |
| `gravity.emotional_density=medium` | cut | Scale midpoint of a field that is itself weakly grounded; cut with the field (density is expressible as emotion_subtone cardinality plus valence=mixed). |
| `gravity.viscosity=medium` | keep | scale midpoint; keep if the field is kept (see viscosity merge with temporal_decay) |
| `gravity.viscosity=fluid` | cut | Nominal value mixed into an ordinal scale (low/medium/high/enduring). Not a persistence level. Cut; use low. |
| `gravity.tether_type=ritual` | keep | Ritual / commemorative memory (Durkheim; Halbwachs 1925 collective memory; Connerton 1989 "How Societies Remember") [KNOWLEDGE] is absent from the individual-level frameworks listed. Keep as EDM-specific; strong presence in the significance literature. |
| `gravity.tether_type=tradition` | keep | see ritual |
| `gravity.recurrence_pattern=emerging` | cut | Not a recurrence structure; overlaps adaptation_trajectory=emerging. Cut. |
| `gravity.temporal_decay=moderate` | keep | scale midpoint; field proposed to merge into persistence |
| `gravity.adaptation_trajectory=stable` | keep | scale midpoint |
| `gravity.adaptation_trajectory=emerging` | cut | Not a trajectory direction; cut (keep improving/stable/declining/integrative). |
| `impulse.social_visibility=private` | cut | Field duplicates constellation.relational_perspective and meta.visibility. Cut field. |
| `impulse.risk_posture=balanced` | keep | scale midpoint |
| `impulse.agency_level=medium` | keep | scale midpoint |
| `impulse.regulation_state=wavering` | keep | scale midpoint |
| `impulse.coping_style=ritualize` | keep | Religious / spiritual coping (Pargament 1997; RCOPE, Pargament, Koenig & Perez 2000) [KNOWLEDGE] is not in Lazarus & Folkman Ways of Coping nor Gross. Keep as EDM-specific; well attested in the coping literature. |

### A2 — Weakly grounded fields (related-only) and duplicate fields: decisions

| Field | Grounding | Decision | Reason |
|---|---|---|---|
| `core.anchor` | weak | keep | Subject/object of the experience. No framework names it as a field, but EmotionML reference@targetedAt and OCC object branches are structural homes. Keep as narrative.subject. |
| `core.wound` | weak | keep | Harm/loss appraisal is in Lazarus and MFOEM (appraisal of loss) but no framework has a free-text "wound" slot. Keep; rename narrative.loss_or_harm. |
| `core.fuel` | weak | keep | Energising motive; SEEKING / SDT intrinsic motivation are the nearest. Keep; rename narrative.drive. |
| `core.bridge` | weak | keep | Past-present integration link; nearest is McAdams meaning-making / Singer integrative meaning, which are already the homes of expressed_insight. Candidate to merge into insight. Keep provisionally. |
| `core.echo` | weak | merge | Duplicates gravity.recall_triggers (retrieval cue) semantically. Merge into salience.retrieval_cues. |
| `core.narrative` | weak | keep | The narrative text itself; the unit of analysis for McAdams/Bruner/Pillemer. Keep as narrative.summary. |
| `constellation.higher_order_emotion` | weak | merge | Free-text complex emotion; coded emotion systems (MFOEM, Cowen & Keltner) already contain awe, nostalgia, etc. Merge into emotion.secondary (coded). |
| `constellation.meta_emotional_state` | weak | keep | Meta-emotion (Gottman et al. 1996; Mitmansgruber et al. 2009) [KNOWLEDGE] is absent from the listed frameworks except as EI competencies. Keep as EDM-specific; candidate for experiment. |
| `constellation.interpersonal_affect` | weak | cut | Free text with no framework home beyond EI competencies; interpersonal circumplex (Leary 1957) [KNOWLEDGE] would be the proper home. Cut or move to extensions. |
| `constellation.narrative_arc` | weak | merge | Overlaps arc_type (transformation appears in both) and tone_shift. Merge the two arc fields into one coded narrative.arc list. |
| `constellation.relational_dynamics` | weak | keep | Relationship category of the experience; no framework enumerates these, but Fiske models are the coded view. Keep, dedupe (friend/friendship, couple/romantic_partnership, drop grief and self_reflection which are not relationships). |
| `constellation.temporal_context` | weak | keep | Life-stage; Conway lifetime periods are thematic, Erikson stages (not in list) are age-banded. Keep as context.life_stage. |
| `constellation.memory_type` | weak | keep | Pillemer event types and Singer SDM are the homes; recode values to Pillemer originating / turning point / anchoring / analogous + ESK. |
| `constellation.media_format` | weak | cut | Administrative; duplicates meta.source_type. |
| `constellation.narrative_archetype` | weak | cut | See value decisions: marketing archetype set, move to extensions. |
| `constellation.symbolic_anchor` | weak | merge | Duplicates core.anchor / tether_type=symbol,object. Merge into narrative.subject or salience.tether. |
| `constellation.relational_perspective` | weak | keep | Bronfenbrenner nested systems are the coded view; dedupe with impulse.directionality and social_visibility. |
| `constellation.temporal_rhythm` | weak | keep | EDM-specific phenomenological time; keep reduced set (see value decisions). |
| `constellation.arc_type` | weak | keep | Best-grounded narrative field (Booker, Campbell, McAdams). Keep as narrative.arc; absorb narrative_arc. |
| `milky_way.event_type` | weak | keep | Keep; recommend Singer & Blagov / Thorne & McLean content categories as a coded companion. |
| `milky_way.location_context` | weak | keep | Episodic "where"; keep as context.place. |
| `milky_way.associated_people` | weak | keep | Episodic "who"; keep as context.people. |
| `gravity.emotional_density` | weak | cut | No framework construct; emotion_subtone cardinality and valence=mixed express it. |
| `gravity.viscosity` | weak | merge | Persistence of affect (Davidson 1998 affective chronometry) [KNOWLEDGE] not in listed frameworks; merge with temporal_decay into salience.persistence (ordinal). |
| `gravity.gravity_type` | weak | merge | Free text duplicating tether_type; Lazarus ego-involvement types are the coded view. Merge into salience.tether. |
| `gravity.tether_type` | weak | keep | Keep as salience.tether; person/event/object map to OCC branches; ritual/tradition are EDM-specific. |
| `gravity.nearby_themes` | weak | keep | Thematic linkage (Conway); keep as salience.themes. |
| `gravity.recurrence_pattern` | weak | keep | Singer specificity (specific vs summary) is the coded view; keep as salience.recurrence. |
| `gravity.strength_score` | weak | keep | SDM criterion "linked to similar memories" is the nearest; EDM-specific network-binding score. Keep; candidate for experiment. |
| `gravity.temporal_decay` | weak | merge | merge into salience.persistence |
| `gravity.resilience_markers` | weak | keep | Positive reappraisal / positive outlook / optimism are coded homes for individual markers; keep as salience.resilience with a coded list. |
| `gravity.adaptation_trajectory` | weak | keep | McAdams redemption/contamination are the coded view; keep reduced set. |
| `impulse.primary_energy` | weak | cut | Duplicates emotion.primary (same example values). Cut. |
| `impulse.directionality` | weak | merge | Duplicates relational_perspective; merge. |
| `impulse.social_visibility` | weak | cut | Duplicates relational_perspective and meta.visibility. |
| `impulse.risk_posture` | weak | keep | Threat vs challenge appraisal (Lazarus) is the coded view; keep as motivation.risk_posture. |

## Gap list B — Framework constructs with no EDM home

| Framework(s) | Construct | Decision | Reason / target |
|---|---|---|---|
| ekman / plutchik / goemotions / mfoem | disgust | add | Basic emotion in every discrete framework; MFOEM:000019. Add to emotion canonical list. |
| ekman / plutchik / goemotions / mfoem | surprise | add | Basic emotion; MFOEM:000032 (positive/negative surprise subclasses). Add. |
| ekman (7) / occ / mfoem | contempt | add | MFOEM:000018. Add. |
| occ / scherer / lazarus / mfoem | guilt | add | Distinct from shame in every appraisal framework; MFOEM:000053. Add. |
| cowen_keltner / goemotions / scherer | interest / curiosity | add | MFOEM:000033 interest, MFOEM:000167 curiosity. Add (replaces part of "wonder"). |
| cowen_keltner / hume / plutchik dyad | awe | add | Keltner & Haidt 2003 [KNOWLEDGE]; Cowen & Keltner category; Plutchik dyad. Add as the coded home for EDM "wonder" / "reverence". |
| goemotions / occ / scherer / mfoem | love | add | MFOEM:000048 (disposition). Add; coded home for "tenderness". |
| cowen_keltner / hume | nostalgia | add | Frequently the dominant affect of autobiographical recall (Sedikides & Wildschut) [KNOWLEDGE]; coded home for "longing". Add. |
| mfoem / goemotions | loneliness; grief; regret / remorse; embarrassment; envy; jealousy; boredom; amusement; contentment; compassion; trust | add | All have MFOEM or GoEmotions codes. Adopt the full MFOEM emotion-process list as the coded vocabulary instead of extending the canonical 17. |
| panksepp | LUST; PLAY | out_of_scope | LUST: sexual content raises PII tier and consent issues; PLAY is covered by amusement/joy. Not added as fields. |
| russell / pad / scherer GRID / barrett / nrc VAD / emotionml | arousal / activation | add | The second axis of every dimensional model has no EDM home (emotional_weight is intensity; urgency is an appraisal). Add emotion.arousal (EmotionML pad-dimensions#arousal). |
| scherer GRID | unpredictability / novelty | covered | Partially covered by temporal_rhythm=sudden and spark. Could become an appraisal.novelty code (MFOEM:000057). |
| pad / nrc VAD / scherer | dominance / power | covered | Covered by impulse.agency_level. |
| scherer SECs / lazarus secondary / occ / mfoem | causal attribution (self / other / chance); intent | add | No EDM home. Add appraisal.attribution coded to MFOEM:000075-000084. Explicit content only ("I blamed myself"). |
| scherer / mfoem | norm / ideal compatibility | covered | Partly covered by arc_type=moral_awakening and emotion shame/guilt/pride. Optional appraisal.norm_compatibility (MFOEM:000094). |
| lazarus secondary appraisal | future expectancy | covered | Covered by emotion hope and adaptation_trajectory. |
| lazarus primary appraisal | goal relevance / congruence | covered | Covered by emotional_weight (relevance) and valence (congruence). |
| occ | fortunes-of-others (happy-for, pity, gloating, resentment) | covered | Covered by free-text emotion values; coded via OCC vocabulary in EmotionML occ-categories. |
| scherer CPM / mfoem / hume facial descriptions | motor expression (facial, vocal) | out_of_scope | Requires observation or inference from media, prohibited by the interpretation-only constraint. Stays out. |
| scherer CPM / mfoem | physiological response | covered | Covered by somatic_signature (stated sensations only). |
| emotionml | confidence attribute | add | EmotionML attaches confidence to every annotation; EDM has no per-field confidence. Add to telemetry (per-field) or as a sibling of each coded value. |
| emotionml | experiencedBy / expressedBy roles | out_of_scope | EDM assumes the source is the experiencer; third-party emotions are not extracted. |
| emotionml | <trace> time-varying intensity | covered | Covered coarsely by temporal_rhythm. |
| mfoem | mood process (vs emotion process) | covered | Covered by viscosity=enduring; recommend an explicit emotion.kind = emotion | mood | feeling code (MFOEM:000001 / 000193 / 000006). |
| mfoem | emotion disposition / personality trait | out_of_scope | Person-level; not an event property. |
| pillemer / bluck | memory functions (directive, self, social) | add | Well-attested (Pillemer 1992; Bluck 2003) and absent from EDM. Add salience.function (multi-valued) when the subject states why the memory matters. |
| singer_blagov | content categories (relationships, life-threatening events, recreation/exploration, achievement/mastery, guilt/shame) | add | Adopt as the coded companion of context.event_type. |
| singer_blagov | specificity (specific vs summary) | covered | Covered by recurrence_pattern (isolated vs cyclical). |
| conway | lifetime periods / general events / ESK hierarchy | covered | Covered by temporal_context + memory_type + recurrence. |
| conway | correspondence vs coherence | out_of_scope | Theoretical property of the memory system, not of an artifact. |
| tulving | remember / know; autonoetic awareness | out_of_scope | Metamemory judgement; would require inference unless stated. |
| damasio | proto / core / autobiographical self | out_of_scope | Levels of consciousness; not an artifact property. |
| barrett | emotional granularity | out_of_scope | Person-level trait. |
| mcadams | nuclear episodes: high point / low point | covered | Covered by valence + memory_type=milestone; could be a coded memory_type value. |
| mcadams | redemption / contamination sequence | covered | Covered by tone_shift (finer) and adaptation_trajectory. |
| mcadams | generativity script | covered | Covered by motivational_orientation=meaning and temporal_focus=future. |
| bruner | ten features of narrative | out_of_scope | Properties of narrative discourse, not of the experience; canonicity-and-breach is reflected in spark. |
| booker | Rags to Riches; The Quest; Comedy | covered | Covered by arc_type (discovery, reconciliation) and narrative_arc=overcoming; add quest if arc list is recoded to Booker. |
| campbell | full 17-stage sequence | covered | arc_type threshold / exile / liberation map to specific stages; the rest is out of scope (story-structure granularity). |
| fiske | communal sharing / authority ranking / equality matching / market pricing | add | Add as the coded view of relational_dynamics (context.relationship_model). |
| bartholomew / ecr | attachment anxiety / avoidance dimensions | out_of_scope | Dimensional attachment would require inference; the categorical field already requires explicit statement. |
| bronfenbrenner | exosystem; chronosystem | covered | Covered by relational_perspective (community) and temporal_context. |
| gross | extended model stages (identification / selection / implementation) | out_of_scope | Process stages of regulation, not stateable properties. |
| sdt | motivation continuum (external ... intrinsic) | out_of_scope | Requires inference about regulation type unless explicitly stated; could be an optional coded value of motivational_orientation. |
| elliot | performance-approach / performance-avoidance goals | out_of_scope | Achievement-goal granularity beyond EDM scope; mastery is covered. |
| mayer_salovey / goleman / bar_on | EI competencies and branches | out_of_scope | Person-level abilities and traits, not event properties. Relevant to the therapeutic partner profile as derived analytics, not to the artifact. |
| wordnet_affect | trait; cognitive state; physical state; hedonic signal; attitude | out_of_scope | a-labels for lexical typing; EDM covers emotion, mood, situation, response, sensation. |
| senticnet | Attention; Aptitude (Hourglass dimensions) | covered | Attention ~ interest/anticipation (emotion); Aptitude ~ trust/admiration. Covered by coded emotion values. |
| snomed | clinical mood findings | out_of_scope | Clinical classification belongs in CROSSWALKS (DSM5_specifiers neighbour), not in the affective core. |
