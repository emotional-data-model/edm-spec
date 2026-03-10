// scripts/validate-examples.mjs
import { readFile } from "node:fs/promises";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const SCHEMA_PATH = new URL("../schema/edm.v0.6.schema.json", import.meta.url);

// Example files with their expected profile values
const EXAMPLES = [
  { file: "examples/example-essential-profile.json", expectedProfile: "essential" },
  { file: "examples/example-extended-profile.json", expectedProfile: "extended" },
  { file: "examples/example-full-profile.json", expectedProfile: "full" },
];

async function main() {
  const schema = JSON.parse(await readFile(SCHEMA_PATH, "utf8"));

  const ajv = new Ajv({
    allErrors: true,
    strict: true,
    allowUnionTypes: true
  });
  addFormats(ajv);

  const validate = ajv.compile(schema);

  if (EXAMPLES.length === 0) {
    console.log("ℹ️  No example files configured.");
    process.exit(0);
  }

  let failures = 0;

  for (const { file, expectedProfile } of EXAMPLES) {
    const data = JSON.parse(await readFile(new URL(`../${file}`, import.meta.url), "utf8"));
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
