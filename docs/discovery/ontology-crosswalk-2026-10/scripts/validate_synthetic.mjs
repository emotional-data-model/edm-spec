// Validate the discovery artifacts with ajv (draft-07, every $ref resolved from local files; no network).
//
//   node scripts/validate_synthetic.mjs v083 <repo-root> <examples-dir>
//       validates <examples-dir>/*.json against schema/edm.v0.8.{essential,extended,full}.schema.json,
//       partner profiles against their base profile exactly as scripts/validate-examples.mjs does.
//
//   node scripts/validate_synthetic.mjs v09 <repo-root> <migrated-dir> <draft-schema-dir> [--strict]
//       validates <migrated-dir>/*.json against the draft v0.9 composites in <draft-schema-dir>.
//       Partner profiles that opt into the trait block (manifest below) are validated against
//       base + trait. --strict skips that composition so the opt-in failure is visible.
//
// Discovery tooling; not part of the published validator. Uses the repo's ajv + ajv-formats.
import { readFile, readdir } from "node:fs/promises";
import { join, resolve } from "node:path";
import { createRequire } from "node:module";

const [mode, repoRoot, examplesDir, draftDir, ...flags] = process.argv.slice(2);
if (!mode || !repoRoot || !examplesDir) {
  console.error("usage: validate_synthetic.mjs v083 <repo-root> <examples-dir> | v09 <repo-root> <migrated-dir> <draft-schema-dir> [--strict]");
  process.exit(2);
}
const require = createRequire(join(resolve(repoRoot), "package.json"));
const Ajv = require("ajv");
const addFormats = require("ajv-formats");

const BASE = {
  "partner:com.deepadata.journaling.v1": "extended",
  "partner:com.deepadata.therapy.v1": "full",
  "partner:com.deepadata.companion.v1": "extended",
  "partner:com.deepadata.wiki.v1": "extended",
};
// v0.9 partner opt-in manifest (discovery assumption): only the therapy profile lists trait.* in included_fields.
const TRAIT_OPT_IN = new Set(["partner:com.deepadata.therapy.v1"]);

async function loadJson(p) { return JSON.parse(await readFile(p, "utf8")); }

async function registerDir(ajv, dir, baseUri) {
  for (const f of (await readdir(dir)).filter((x) => x.endsWith(".json"))) {
    const s = await loadJson(join(dir, f));
    ajv.addSchema(s, s.$id || `${baseUri}/${f}`);
  }
}

function newAjv() {
  const ajv = new Ajv({ allErrors: true, strict: false, allowUnionTypes: true });
  addFormats(ajv);
  return ajv;
}

async function main() {
  const ajv = newAjv();
  const validators = {};
  let schemaLabel;
  if (mode === "v083") {
    const schemaDir = join(repoRoot, "schema");
    await registerDir(ajv, join(schemaDir, "fragments"), "https://deepadata.com/schemas/edm/v0.8.0/fragments");
    for (const p of ["essential", "extended", "full"]) {
      const s = await loadJson(join(schemaDir, `edm.v0.8.${p}.schema.json`));
      ajv.addSchema(s, s.$id);
      validators[p] = ajv.compile(s);
    }
    schemaLabel = "schema/edm.v0.8.*.schema.json";
  } else if (mode === "v09") {
    const strict = flags.includes("--strict");
    // the draft composites reuse the unchanged v0.8.0 infrastructure fragments by reference
    await registerDir(ajv, join(repoRoot, "schema", "fragments"), "https://deepadata.com/schemas/edm/v0.8.0/fragments");
    await registerDir(ajv, join(draftDir, "fragments"), "https://deepadata.com/schemas/edm/v0.9.0-draft/fragments");
    for (const p of ["essential", "extended", "full"]) {
      const s = await loadJson(join(draftDir, `edm.v0.9.${p}.schema.json`));
      ajv.addSchema(s, s.$id);
      validators[p] = ajv.compile(s);
      if (!strict) {
        // base + opt-in trait block, as a partner manifest listing trait.* would resolve to
        const withTrait = structuredClone(s);
        withTrait.$id = s.$id.replace(".schema.json", ".with-trait.schema.json");
        withTrait.title += " + opt-in trait";
        withTrait.properties.trait = { $ref: "https://deepadata.com/schemas/edm/v0.9.0-draft/fragments/trait.json" };
        ajv.addSchema(withTrait, withTrait.$id);
        validators[p + "+trait"] = ajv.compile(withTrait);
      }
    }
    schemaLabel = `${draftDir}/edm.v0.9.*.schema.json${strict ? " (strict, no trait opt-in)" : ""}`;
  } else {
    console.error(`unknown mode ${mode}`); process.exit(2);
  }

  const files = (await readdir(examplesDir)).filter((f) => f.endsWith(".json")).sort();
  let failures = 0;
  const rows = [];
  for (const f of files) {
    const data = await loadJson(join(examplesDir, f));
    const profile = data?.meta?.profile;
    const base = BASE[profile] || profile;
    let key = base;
    if (mode === "v09" && TRAIT_OPT_IN.has(profile) && validators[base + "+trait"]) key = base + "+trait";
    const validate = validators[key];
    if (!validate) { failures++; rows.push([f, profile, key, "NO VALIDATOR"]); continue; }
    const ok = validate(data);
    if (ok) rows.push([f, profile, key, "valid"]);
    else {
      failures++;
      const errs = validate.errors.map((e) => `${e.instancePath || "/"} ${e.message}${e.params?.additionalProperty ? ` (${e.params.additionalProperty})` : ""}${e.params?.allowedValues ? ` [${e.params.allowedValues.join(", ")}]` : ""}`);
      rows.push([f, profile, key, "INVALID: " + [...new Set(errs)].join(" | ")]);
    }
  }
  console.log(`mode=${mode} schemas=${schemaLabel} examples=${examplesDir}`);
  for (const r of rows) console.log(`  ${r[0]} | ${r[1]} | validated as ${r[2]} | ${r[3]}`);
  console.log(`${files.length - failures}/${files.length} valid`);
  process.exit(failures ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(2); });
