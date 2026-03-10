// scripts/validate-examples.mjs
import { readFile, readdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCHEMA_DIR = join(__dirname, "../schema");
const SCHEMA_PATH = join(SCHEMA_DIR, "edm.v0.6.schema.json");

// Base URL used in the main schema's $id
const SCHEMA_BASE_URL = "https://deepadata.com/schemas/edm/v0.6.0";

// Example files with their expected profile values
const EXAMPLES = [
  { file: "example-essential-profile.json", expectedProfile: "essential" },
  { file: "example-extended-profile.json", expectedProfile: "extended" },
  { file: "example-full-profile.json", expectedProfile: "full" },
];

async function main() {
  const ajv = new Ajv({
    allErrors: true,
    strict: false,  // Allow x_* extension keywords
    allowUnionTypes: true
  });
  addFormats(ajv);

  // Load fragment schemas with full URLs as keys (matching how main schema references them)
  const fragmentsDir = join(SCHEMA_DIR, "fragments");
  const fragmentFiles = await readdir(fragmentsDir);
  
  for (const file of fragmentFiles) {
    if (file.endsWith(".json")) {
      const fragmentPath = join(fragmentsDir, file);
      const fragment = JSON.parse(await readFile(fragmentPath, "utf8"));
      // Register with absolute URI matching how main schema references them
      const absoluteUri = `${SCHEMA_BASE_URL}/fragments/${file}`;
      ajv.addSchema(fragment, absoluteUri);
    }
  }

  // Load and compile main schema
  const schema = JSON.parse(await readFile(SCHEMA_PATH, "utf8"));
  const validate = ajv.compile(schema);

  if (EXAMPLES.length === 0) {
    console.log("ℹ️  No example files configured.");
    process.exit(0);
  }

  let failures = 0;
  const examplesDir = join(__dirname, "../examples");

  for (const { file, expectedProfile } of EXAMPLES) {
    const filePath = join(examplesDir, file);
    const data = JSON.parse(await readFile(filePath, "utf8"));
    const schemaValid = validate(data);

    // Check schema validation
    if (!schemaValid) {
      failures++;
      console.log(`❌ Schema invalid: ${file}`);
      console.log(
        ajv.errorsText(validate.errors, { separator: "\n  - " })
      );
      continue;
    }

    // Check meta.profile matches expected value
    const actualProfile = data?.meta?.profile;
    if (actualProfile !== expectedProfile) {
      failures++;
      console.log(`❌ Profile mismatch: ${file}`);
      console.log(`   Expected meta.profile: "${expectedProfile}"`);
      console.log(`   Actual meta.profile: "${actualProfile}"`);
      continue;
    }

    console.log(`✅ Valid: ${file} (profile: ${actualProfile})`);
  }

  if (failures > 0) {
    console.error(`\n✖ ${failures} file(s) failed validation.`);
    process.exit(1);
  } else {
    console.log("\n✓ All example files are valid against edm.v0.6 with correct profile values.");
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
