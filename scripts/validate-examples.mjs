// scripts/validate-examples.mjs
import { readFile, readdir, access } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = join(__dirname, "..");
const SCHEMA_DIR = join(ROOT_DIR, "schema");

// ---------------------------------------------------------------------------
// Single source of truth: package.json version. Everything below derives from
// it — no hardcoded schema version strings anywhere in this script.
// ---------------------------------------------------------------------------
const pkg = JSON.parse(await readFile(join(ROOT_DIR, "package.json"), "utf8"));
const PKG_VERSION = pkg.version;                       // e.g. "0.8.1"
const [MAJOR, MINOR] = PKG_VERSION.split(".");          // "0", "8"
const VERSION_LINE = `${MAJOR}.${MINOR}`;               // "0.8"

// Schema $id base uses the major.minor line pinned at patch .0 (per the $id
// convention in schema/edm.v*.schema.json and schema/fragments/*).
const SCHEMA_BASE_URL = `https://deepadata.com/schemas/edm/v${VERSION_LINE}.0`;

// Profile schema filenames derive from the version line:
//   edm.v<major>.<minor>.<profile>.schema.json
const PROFILES = ["essential", "extended", "full"];
const PROFILE_SCHEMAS = Object.fromEntries(
  PROFILES.map((p) => [p, `edm.v${VERSION_LINE}.${p}.schema.json`])
);

// Example files with their expected profile values.
//
// `expectedProfile` must equal the artifact's meta.profile. For partner
// profiles (meta.profile starts with "partner:"), `baseProfile` names the
// canonical profile schema (essential/extended/full) the artifact is validated
// against, per ADR-0017 — a partner profile is a field manifest over a base.
const EXAMPLES = [
  { file: "example-essential-profile.json", expectedProfile: "essential" },
  { file: "example-extended-profile.json", expectedProfile: "extended" },
  { file: "example-full-profile.json", expectedProfile: "full" },
  {
    file: "example-partner-journaling.json",
    expectedProfile: "partner:com.deepadata.journaling.v1",
    baseProfile: "extended",
  },
  {
    file: "example-partner-therapy.json",
    expectedProfile: "partner:com.deepadata.therapy.v1",
    baseProfile: "full",
  },
  {
    file: "example-partner-companion.json",
    expectedProfile: "partner:com.deepadata.companion.v1",
    baseProfile: "extended",
  },
  {
    file: "example-partner-wiki.json",
    expectedProfile: "partner:com.deepadata.wiki.v1",
    baseProfile: "extended",
  },
];

// Fail fast with a clear error if the derived schema files are not present.
async function assertSchemasExist() {
  const missing = [];
  for (const [profile, schemaFile] of Object.entries(PROFILE_SCHEMAS)) {
    const schemaPath = join(SCHEMA_DIR, schemaFile);
    try {
      await access(schemaPath);
    } catch {
      missing.push({ profile, schemaFile, schemaPath });
    }
  }
  if (missing.length > 0) {
    const lines = missing.map(
      (m) => `  - ${m.profile}: ${m.schemaFile} (expected at ${m.schemaPath})`
    );
    throw new Error(
      `Derived schema file(s) not found:\n${lines.join("\n")}\n` +
        `Derived from package.json version "${PKG_VERSION}" (line v${VERSION_LINE}).\n` +
        `Verify schema/ contains edm.v${VERSION_LINE}.{${PROFILES.join(",")}}.schema.json, ` +
        `or correct the version in package.json.`
    );
  }
}

async function loadFragments(ajv) {
  const fragmentsDir = join(SCHEMA_DIR, "fragments");
  const fragmentFiles = await readdir(fragmentsDir);

  for (const file of fragmentFiles) {
    if (file.endsWith(".json")) {
      const fragmentPath = join(fragmentsDir, file);
      const fragment = JSON.parse(await readFile(fragmentPath, "utf8"));
      // Register with absolute URI matching how the profile schemas $ref them.
      const absoluteUri = `${SCHEMA_BASE_URL}/fragments/${file}`;
      ajv.addSchema(fragment, absoluteUri);
    }
  }
}

async function loadProfileSchemas(ajv) {
  const validators = {};

  for (const [profile, schemaFile] of Object.entries(PROFILE_SCHEMAS)) {
    const schemaPath = join(SCHEMA_DIR, schemaFile);
    const schema = JSON.parse(await readFile(schemaPath, "utf8"));
    // Register under the schema's own $id (falling back to a derived URI).
    const fallbackUri = `${SCHEMA_BASE_URL}/${schemaFile}`;
    ajv.addSchema(schema, schema.$id || fallbackUri);
    validators[profile] = ajv.compile(schema);
  }

  return validators;
}

async function main() {
  await assertSchemasExist();

  const ajv = new Ajv({
    allErrors: true,
    strict: false, // Allow x_* extension keywords
    allowUnionTypes: true,
  });
  addFormats(ajv);

  // Load fragment schemas first
  await loadFragments(ajv);

  // Load and compile profile-specific schemas
  const validators = await loadProfileSchemas(ajv);

  if (EXAMPLES.length === 0) {
    console.log("No example files configured.");
    process.exit(0);
  }

  let failures = 0;
  const examplesDir = join(ROOT_DIR, "examples");

  for (const { file, expectedProfile, baseProfile } of EXAMPLES) {
    const filePath = join(examplesDir, file);
    const data = JSON.parse(await readFile(filePath, "utf8"));

    // Check meta.profile matches expected value first
    const actualProfile = data?.meta?.profile;
    if (actualProfile !== expectedProfile) {
      failures++;
      console.log(`Profile mismatch: ${file}`);
      console.log(`   Expected meta.profile: "${expectedProfile}"`);
      console.log(`   Actual meta.profile: "${actualProfile}"`);
      continue;
    }

    // For partner profiles, validate against the canonical base profile schema.
    // For canonical profiles, the profile value is also the schema key.
    const schemaProfile = baseProfile || actualProfile;

    // Enforce the single-source principle: example version derives from (must
    // equal) the package version. This catches drift the schema pattern alone
    // (^0\.<minor>\.[0-9]+$) would let through.
    const actualVersion = data?.meta?.version;
    if (actualVersion !== PKG_VERSION) {
      failures++;
      console.log(`Version drift: ${file}`);
      console.log(`   Expected meta.version: "${PKG_VERSION}" (from package.json)`);
      console.log(`   Actual meta.version: "${actualVersion}"`);
      continue;
    }

    // Get the validator for the (base) profile schema
    const validate = validators[schemaProfile];
    if (!validate) {
      failures++;
      console.log(`No validator for profile: ${schemaProfile} in ${file}`);
      continue;
    }

    // Validate against profile-specific schema
    const schemaValid = validate(data);

    if (!schemaValid) {
      failures++;
      console.log(`Schema invalid: ${file} (profile: ${actualProfile})`);
      console.log(ajv.errorsText(validate.errors, { separator: "\n  - " }));
      continue;
    }

    const schemaNote =
      schemaProfile === actualProfile
        ? `schema: ${PROFILE_SCHEMAS[schemaProfile]}`
        : `base: ${schemaProfile}, schema: ${PROFILE_SCHEMAS[schemaProfile]}`;
    console.log(`Valid: ${file} (profile: ${actualProfile}, ${schemaNote})`);
  }

  if (failures > 0) {
    console.error(`\n${failures} file(s) failed validation.`);
    process.exit(1);
  } else {
    console.log(
      `\nAll example files are valid against the v${VERSION_LINE} profile schemas (package version ${PKG_VERSION}).`
    );
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
