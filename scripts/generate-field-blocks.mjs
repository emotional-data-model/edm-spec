#!/usr/bin/env node
/**
 * JSON-Schema → prompt field-block generator (ADR-0030, amended).
 *
 * Spec-level port of the SDK's Phase A generator
 * (deepadata-edm-sdk/src/extractors/generate-field-block.ts). The SDK version
 * walks the zod validator; this one reads the canonical JSON Schema fragments —
 * which are the source of truth (ADR-0030 amended) — so the prompt skeletons
 * downstream tools embed are generated from the spec itself and can never
 * drift from it.
 *
 * The OUTPUT FORMAT is locked: byte-for-byte identical to what the SDK's Phase A
 * generator emits (and therefore to the hand-written skeletons it reproduces).
 *
 * Classification maps directly from JSON Schema to the kinds the prompt renders:
 *   - "x-edm-canonical": [...]  → canonical-enum (two-tier; free text accepted)
 *   - "enum": [...]             → strict-enum    (validator rejects non-members)
 *   - bare "type" string/number/boolean/array → free text / number / boolean / array
 *
 * Field MEMBERSHIP and ORDER per profile come from the composite profile schemas
 * (schema/edm.v0.8.{essential,extended,full}.schema.json): which representational
 * domains a profile includes, and — for inline domains — which fields. This is
 * the role the SDK's LlmEssential/LlmExtended/LlmExtractedFields zod schemas play.
 *
 * Field DEFINITIONS (classification + canonical value lists) are always read from
 * the fragments, never from the composite's inline copies, so the canonical
 * vocabulary rendered in each comment is the one the fragment enforces.
 *
 * Zero runtime dependencies beyond Node built-ins. Reads only files inside this
 * repo. Build-time tool, not a library.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCHEMA_DIR = join(__dirname, "..", "schema");
const FRAGMENTS_DIR = join(SCHEMA_DIR, "fragments");

const loadJson = (path) => JSON.parse(readFileSync(path, "utf8"));

// ---------------------------------------------------------------------------
// Profile / domain wiring
// ---------------------------------------------------------------------------

/** The LLM-extracted representational domains, in canonical (zod definition) order. */
const LLM_DOMAINS = ["core", "constellation", "milky_way", "gravity", "impulse"];

const FRAGMENT_FILE = {
  core: "core.json",
  constellation: "constellation.json",
  milky_way: "milky_way.json",
  gravity: "gravity.json",
  impulse: "impulse.json",
};

const COMPOSITE_FILE = {
  essential: "edm.v0.8.essential.schema.json",
  extended: "edm.v0.8.extended.schema.json",
  full: "edm.v0.8.full.schema.json",
};

export const PROFILES = ["essential", "extended", "full"];

const loadFragment = (domain) => loadJson(join(FRAGMENTS_DIR, FRAGMENT_FILE[domain]));

/**
 * experiential_stance is a top-level extraction-only field — never sealed into
 * the artifact body, so it appears in no fragment or composite schema. The SDK
 * carries it as ExperientialStanceSchema (z.enum). Mirror it here as a strict
 * enum so the generated block asks for it exactly as the current prompts do.
 */
const EXPERIENTIAL_STANCE_DEF = {
  enum: ["lived", "witnessed", "quoted_third_party", "assistant_generated", "hypothetical"],
};

// ---------------------------------------------------------------------------
// Classification — JSON Schema → field kind
// ---------------------------------------------------------------------------

/**
 * @typedef {"strict-enum"|"canonical-enum"|"string"|"number"|"boolean"|"string-array"} FieldKind
 * @typedef {{ kind: FieldKind, enumValues?: string[] }} FieldInfo
 */

/** @returns {FieldInfo} */
function classifyField(def) {
  if (Array.isArray(def["x-edm-canonical"])) {
    return { kind: "canonical-enum", enumValues: def["x-edm-canonical"] };
  }
  if (Array.isArray(def.enum)) {
    // JSON Schema enums carry a trailing `null` for nullable fields; zod models
    // nullability with `.nullable()` and keeps it out of the enum, so strip it.
    return { kind: "strict-enum", enumValues: def.enum.filter((v) => v !== null) };
  }
  const types = Array.isArray(def.type) ? def.type : [def.type];
  if (types.includes("number") || types.includes("integer")) return { kind: "number" };
  if (types.includes("boolean")) return { kind: "boolean" };
  if (types.includes("array")) return { kind: "string-array" };
  return { kind: "string" };
}

// ---------------------------------------------------------------------------
// Presentation layer (OUTPUT_CONTRACT — hand-written, §4)
//
// Ported verbatim from the SDK's generate-field-block.ts. Enum VALUES are NEVER
// in these tables — they come from the fragment. Only presentation the schema
// does not carry — prose guidance for free-text fields, suffix wording,
// alignment — lives here.
// ---------------------------------------------------------------------------

const STRICT_SUFFIX = " (pick ONE or null)";
const CANONICAL_SUFFIX = " (free text accepted if none fits)";

/** Per-field suffix overrides for strict enums (keyed `domain.field`). */
const SUFFIX_OVERRIDE = {
  "constellation.narrative_archetype": " (pick ONE or null; lowercase)",
};

/** Extra prose appended after a canonical-enum comment. */
const CANONICAL_TRAILING = {
  "constellation.arc_type":
    ". gratitude = moments of thankfulness, appreciation, acknowledging blessing; authenticity = feeling fully oneself, self-alignment, identity congruence",
};

/** Prose guidance for non-enum (free text / number / boolean / array) fields. */
const GUIDANCE = {
  // core
  "core.anchor": 'central theme (e.g., "dad\'s toolbox", "nana\'s traditions")',
  "core.spark": 'what triggered the memory (e.g., "finding the cassette", "first snow")',
  "core.wound":
    "The specific vulnerability, loss, or pain present — NOT generic labels like 'loss' or 'grief' but what exactly was lost or why it hurts. Examples: 'unlived travel dream', 'war silence never spoken', 'father died before I knew him', 'shame of not fitting in'. If no wound is present, use null.",
  "core.fuel": 'what energized the experience (e.g., "shared laughter", "curiosity")',
  "core.bridge":
    'connection between past and present (e.g., "replaying old tape", "returning to the porch")',
  "core.echo": 'what still resonates (e.g., "her laugh", "smell of oil", "city lights on water")',
  "core.narrative":
    "3–5 sentences. REQUIRED: include ALL of the following — ≥1 concrete sensory detail (sight, sound, smell, texture), ≥1 temporal cue that anchors the memory in time, ≥1 symbolic callback that connects past to present. Write from the subject's perspective. Do not compress or summarise — give the memory space to breathe. Faithful and specific. Never generic.",
  // constellation
  "constellation.emotion_subtone": "2–4 short words (e.g., bittersweet, grateful) — free text array",
  "constellation.higher_order_emotion": "free text: e.g., awe, forgiveness, pride, moral_elevation (or null)",
  "constellation.meta_emotional_state": "free text: e.g., acceptance, confusion, curiosity (or null)",
  "constellation.interpersonal_affect": "free text: e.g., warmth, openness, defensiveness (or null)",
  "constellation.symbolic_anchor": "concrete object/place/ritual (or null)",
  "constellation.identity_thread": "short sentence",
  "constellation.expressed_insight": "brief insight explicitly stated by subject (extracted, not inferred)",
  "constellation.transformational_pivot": "true if subject explicitly identifies this as life-changing",
  "constellation.somatic_signature":
    'bodily sensations explicitly described (e.g., "chest tightness", "warmth spreading") or null',
  // milky_way
  "milky_way.event_type": "e.g., family gathering, farewell, birthday (or null)",
  "milky_way.location_context": "place from text or image (or null)",
  "milky_way.associated_people": "names or roles (proper case allowed)",
  "milky_way.tone_shift": "e.g., loss to gratitude (or null)",
  // gravity
  "gravity.emotional_weight":
    "0.0–1.0 (felt intensity IN THE MOMENT). Calibration: 0.9+ life-altering irreversible moments; 0.7-0.9 significant personal events with strong emotional response; 0.4-0.7 meaningful but routine emotional experiences; 0.1-0.4 mild passing emotional content",
  "gravity.gravity_type": "short phrase (e.g., symbolic resonance)",
  "gravity.recall_triggers": "sensory or symbolic cues (lowercase tokens)",
  "gravity.retrieval_keys": "compact hooks (3–6 tokens recommended)",
  "gravity.nearby_themes": "adjacent concepts",
  "gravity.strength_score": "0.0–1.0 (how BOUND/STUCK this memory is)",
  "gravity.resilience_markers": "1–3 (e.g., acceptance, optimism, continuity)",
  // impulse
  "impulse.primary_energy": "free text: e.g., curiosity, fear, compassion (or null; lowercase)",
  // top-level
  experiential_stance: "", // enum-driven; guidance unused
};

const PLACEHOLDER = {
  "strict-enum": '""',
  "canonical-enum": '""',
  string: '""',
  number: "0.0",
  boolean: "false",
  "string-array": "[]",
};

/** Build the `// ...` comment text for a field, or null if it has none. */
function commentFor(key, info) {
  if (info.kind === "strict-enum") {
    const suffix = SUFFIX_OVERRIDE[key] ?? STRICT_SUFFIX;
    return `STRICT ENUM: ${(info.enumValues ?? []).join(" | ")}${suffix}`;
  }
  if (info.kind === "canonical-enum") {
    const trailing = CANONICAL_TRAILING[key] ?? "";
    return `CANONICAL: ${(info.enumValues ?? []).join(" | ")}${CANONICAL_SUFFIX}${trailing}`;
  }
  const g = GUIDANCE[key];
  return g && g.length > 0 ? g : null;
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

/**
 * @typedef {{ content: string, comment: string|null }} Line
 */

/** Join lines, aligning each block's `//` to (max content length) + 1 space. */
function renderBlock(lines) {
  const maxLen = lines.reduce((m, l) => Math.max(m, l.content.length), 0);
  return lines.map((l) => {
    if (l.comment === null) return l.content;
    const pad = " ".repeat(maxLen - l.content.length + 1);
    return `${l.content}${pad}// ${l.comment}`;
  });
}

/**
 * Resolve a profile domain to its ordered `[fieldName, def]` pairs.
 * Field names/order: inline composite properties when present, else fragment
 * order. Field defs: always the fragment (source of truth), falling back to the
 * inline composite copy only if the fragment lacks the field.
 */
function domainFields(compositeProp, fragment) {
  const fragProps = fragment.properties ?? {};
  const inlineProps = compositeProp && compositeProp.properties;
  const names = inlineProps ? Object.keys(inlineProps) : Object.keys(fragProps);
  return names.map((name) => [name, fragProps[name] ?? (inlineProps ? inlineProps[name] : undefined)]);
}

/**
 * Generate the JSON field-block skeleton for a profile, from the JSON Schema.
 *
 * Output shape (matches the current hand-written skeletons):
 *
 *   {
 *     "experiential_stance": "",  // STRICT ENUM: ...
 *     "core": {
 *       "anchor": "",  // central theme ...
 *       ...
 *     },
 *     ...
 *   }
 */
export function generateFieldBlock(profile) {
  if (!COMPOSITE_FILE[profile]) {
    throw new Error(`unknown profile "${profile}" (expected one of: ${PROFILES.join(", ")})`);
  }
  const composite = loadJson(join(SCHEMA_DIR, COMPOSITE_FILE[profile]));
  const props = composite.properties ?? {};

  // Representational domains present in this profile, in canonical order.
  const domains = LLM_DOMAINS.filter((d) => props[d]);

  // Top-level: the experiential_stance scalar renders first and inline; domains
  // render as nested blocks. (Mirrors the SDK's [...scalars, ...domains] order.)
  const topLevelCount = 1 + domains.length;
  let topIdx = 0;

  const out = ["{"];

  // experiential_stance (scalar)
  {
    const isLastTop = topIdx === topLevelCount - 1;
    const topComma = isLastTop ? "" : ",";
    const info = classifyField(EXPERIENTIAL_STANCE_DEF);
    const comment = commentFor("experiential_stance", info);
    const [rendered] = renderBlock([
      { content: `  "experiential_stance": ${PLACEHOLDER[info.kind]}${topComma}`, comment },
    ]);
    out.push(rendered);
    topIdx++;
  }

  for (const domain of domains) {
    const isLastTop = topIdx === topLevelCount - 1;
    const topComma = isLastTop ? "" : ",";
    const fragment = loadFragment(domain);
    const fields = domainFields(props[domain], fragment);

    out.push(`  "${domain}": {`);
    const lines = fields.map(([field, def], idx) => {
      const isLastField = idx === fields.length - 1;
      const comma = isLastField ? "" : ",";
      const info = classifyField(def);
      const comment = commentFor(`${domain}.${field}`, info);
      return { content: `    "${field}": ${PLACEHOLDER[info.kind]}${comma}`, comment };
    });
    out.push(...renderBlock(lines));
    out.push(`  }${topComma}`);
    topIdx++;
  }

  out.push("}");
  return out.join("\n");
}

// ---------------------------------------------------------------------------
// CLI:  node scripts/generate-field-blocks.mjs [essential|extended|full]
// ---------------------------------------------------------------------------

function main(argv) {
  const arg = argv[2];
  if (arg && !PROFILES.includes(arg)) {
    process.stderr.write(
      `error: unknown profile "${arg}"\nusage: node scripts/generate-field-blocks.mjs [${PROFILES.join("|")}]\n`,
    );
    process.exit(1);
  }
  const profiles = arg ? [arg] : PROFILES;
  const blocks = profiles.map((p) => {
    const block = generateFieldBlock(p);
    return profiles.length > 1 ? `// ===== ${p.toUpperCase()} PROFILE =====\n${block}` : block;
  });
  process.stdout.write(blocks.join("\n\n") + "\n");
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  main(process.argv);
}
