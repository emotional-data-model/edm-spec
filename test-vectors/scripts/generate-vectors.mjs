#!/usr/bin/env node
/**
 * Test Vector Generator for .ddna Envelope Verification
 *
 * Generates canonical test vectors per ADR-0020 Phase 2.
 * Uses deterministic test keys from RFC 8032 §7.1 for reproducibility.
 *
 * Path B implementation: standalone signing using @noble/ed25519 directly.
 *
 * Source references:
 * - DDNA_SIGNING_MODEL.md §"Signing Input Construction" (steps 1-7)
 * - DDNA_SIGNING_MODEL.md §"Verification Procedure" (steps 1-7)
 * - RFC 8032 §7.1 (Ed25519 test vectors)
 * - RFC 8785 (JSON Canonicalization Scheme)
 */

import * as ed25519 from '@noble/ed25519';
import { sha512 } from '@noble/hashes/sha512';
import { sha256 } from '@noble/hashes/sha256';
import { base58btc } from 'multiformats/bases/base58';
import canonicalize from 'canonicalize';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

// Configure ed25519 to use sha512
// Source: @noble/ed25519 documentation
ed25519.etc.sha512Sync = (...msgs) => {
  const h = sha512.create();
  for (const msg of msgs) h.update(msg);
  return h.digest();
};

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const VECTORS_DIR = path.resolve(__dirname, '..');

// =============================================================================
// TEST KEYS (RFC 8032 §7.1)
// =============================================================================

/**
 * Test Key 1: RFC 8032 §7.1 Test 1
 * Source: https://www.rfc-editor.org/rfc/rfc8032#section-7.1
 */
const TEST_KEY_1 = {
  privateKey: hexToBytes('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60'),
  publicKey: hexToBytes('d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a'),
};

/**
 * Test Key 2: RFC 8032 §7.1 Test 2
 * Source: https://www.rfc-editor.org/rfc/rfc8032#section-7.1
 */
const TEST_KEY_2 = {
  privateKey: hexToBytes('4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb'),
  publicKey: hexToBytes('3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c'),
};

// =============================================================================
// DID UTILITIES
// =============================================================================

/**
 * Multicodec prefix for Ed25519 public key (0xed01)
 * Source: https://github.com/multiformats/multicodec/blob/master/table.csv
 * Source: deepadata-com/lib/ddna/did.ts:11
 */
const ED25519_MULTICODEC_PREFIX = new Uint8Array([0xed, 0x01]);

/**
 * Encode an Ed25519 public key as a did:key identifier
 * Source: deepadata-com/lib/ddna/did.ts:16-27
 */
function publicKeyToDid(publicKey) {
  const multicodecKey = new Uint8Array(ED25519_MULTICODEC_PREFIX.length + publicKey.length);
  multicodecKey.set(ED25519_MULTICODEC_PREFIX, 0);
  multicodecKey.set(publicKey, ED25519_MULTICODEC_PREFIX.length);
  const encoded = base58btc.encode(multicodecKey);
  return `did:key:${encoded}`;
}

// =============================================================================
// SIGNING UTILITIES
// =============================================================================

/**
 * Construct signing input per DDNA_SIGNING_MODEL.md §"Signing Input Construction"
 *
 * signing_input = SHA-256(JCS(proof_options)) || SHA-256(JCS(document))
 *
 * Source: DDNA_SIGNING_MODEL.md lines 166-224
 */
function constructSigningInput(proofOptions, document) {
  // Step 3: Canonicalize both objects (RFC 8785)
  const canonicalProofOptions = canonicalize(proofOptions);
  const canonicalDocument = canonicalize(document);

  // Step 4: Hash both canonical forms (SHA-256, FIPS 180-4)
  const proofOptionsHash = sha256(new TextEncoder().encode(canonicalProofOptions));
  const documentHash = sha256(new TextEncoder().encode(canonicalDocument));

  // Step 5: Concatenate hashes (64 bytes total)
  const signingInput = new Uint8Array(64);
  signingInput.set(proofOptionsHash, 0);
  signingInput.set(documentHash, 32);

  return signingInput;
}

/**
 * Sign document with Ed25519
 * Source: DDNA_SIGNING_MODEL.md §"Signing Input Construction" Step 6-7
 * Source: RFC 8032 (Ed25519)
 */
function sign(privateKey, signingInput) {
  // Step 6: Sign with Ed25519
  const signature = ed25519.sign(signingInput, privateKey);

  // Step 7: Encode as multibase base58-btc (prefix 'z')
  // Source: DDNA_SIGNING_MODEL.md §"Proof Fields" line 104
  return base58btc.encode(signature);
}

/**
 * Create a complete proof object
 * Source: DDNA_SIGNING_MODEL.md §"Proof Format" lines 80-100
 */
function createProof(privateKey, publicKey, document, created, options = {}) {
  const did = publicKeyToDid(publicKey);

  // Proof options (everything except proofValue)
  // Source: DDNA_SIGNING_MODEL.md §"Proof Fields" lines 97-104
  const proofOptions = {
    type: 'DataIntegrityProof',
    cryptosuite: 'eddsa-jcs-2022',
    created,
    verificationMethod: did,
    proofPurpose: 'assertionMethod',
    ...(options.expires && { expires: options.expires }),
  };

  const signingInput = constructSigningInput(proofOptions, document);
  const proofValue = sign(privateKey, signingInput);

  return {
    ...proofOptions,
    proofValue,
  };
}

// =============================================================================
// PAYLOAD TEMPLATES
// =============================================================================

/**
 * Essential profile payload
 * Source: deepadata-edm-spec/examples/example-essential-profile.json
 */
function createEssentialPayload() {
  return {
    meta: {
      id: 'test-vector-001-essential',
      version: '0.8.0',
      profile: 'essential',
      created_at: '2026-04-22T00:00:00Z',
      owner_user_id: 'test-user-001',
      consent_basis: 'consent',
      visibility: 'private',
      pii_tier: 'moderate',
    },
    core: {
      anchor: 'test anchor',
      spark: 'test spark',
      wound: null,
      fuel: 'test fuel',
      bridge: null,
      echo: 'test echo',
    },
    constellation: {
      emotion_primary: 'joy',
      emotion_subtone: ['grateful'],
      narrative_arc: 'overcoming',
    },
    governance: {
      jurisdiction: 'AU',
      retention_policy: {
        basis: 'user_defined',
        ttl_days: null,
        on_expiry: 'soft_delete',
      },
      subject_rights: {
        portable: true,
        erasable: true,
        explainable: false,
      },
    },
    telemetry: {
      entry_confidence: 1,
      extraction_model: 'test-model',
    },
  };
}

/**
 * Full profile payload (includes all domains)
 */
function createFullPayload() {
  return {
    meta: {
      id: 'test-vector-002-full',
      version: '0.8.0',
      profile: 'full',
      created_at: '2026-04-22T00:00:00Z',
      owner_user_id: 'test-user-002',
      consent_basis: 'consent',
      visibility: 'private',
      pii_tier: 'high',
    },
    core: {
      anchor: 'grandmother',
      spark: 'finding photographs',
      wound: 'loss',
      fuel: 'love',
      bridge: 'memory preservation',
      echo: 'her laugh',
      narrative: 'Visiting grandmother\'s house and finding old photographs...',
    },
    constellation: {
      emotion_primary: 'nostalgia',
      emotion_subtone: ['love', 'grief', 'gratitude'],
      narrative_arc: 'reflection',
    },
    milky_way: {
      memory_type: 'episodic',
      temporal_distance: 'distant',
      vividness: 0.8,
    },
    gravity: {
      weight: 0.9,
      pull_direction: 'past',
    },
    impulse: {
      activation_level: 0.6,
      approach_avoidance: 'approach',
    },
    governance: {
      jurisdiction: 'AU',
      retention_policy: {
        basis: 'user_defined',
        ttl_days: null,
        on_expiry: 'soft_delete',
      },
      subject_rights: {
        portable: true,
        erasable: true,
        explainable: true,
      },
    },
    telemetry: {
      entry_confidence: 0.95,
      extraction_model: 'test-model',
    },
    system: {
      processing_version: '1.0.0',
    },
    crosswalks: {},
  };
}

/**
 * Partner journaling profile payload
 */
function createPartnerJournalingPayload() {
  return {
    meta: {
      id: 'test-vector-003-partner',
      version: '0.8.0',
      profile: 'partner:com.deepadata.journaling.v1',
      created_at: '2026-04-22T00:00:00Z',
      owner_user_id: 'test-user-003',
      consent_basis: 'consent',
      visibility: 'private',
      pii_tier: 'moderate',
    },
    core: {
      anchor: 'daily reflection',
      spark: 'morning routine',
      wound: null,
      fuel: 'self-awareness',
      bridge: null,
      echo: 'calm',
    },
    constellation: {
      emotion_primary: 'contentment',
      emotion_subtone: ['peaceful'],
      narrative_arc: 'stability',
    },
    governance: {
      jurisdiction: 'US',
      retention_policy: {
        basis: 'user_defined',
        ttl_days: 365,
        on_expiry: 'soft_delete',
      },
      subject_rights: {
        portable: true,
        erasable: true,
        explainable: false,
      },
    },
    telemetry: {
      entry_confidence: 1,
      extraction_model: 'journaling-v1',
    },
  };
}

/**
 * Create ddna_header
 * Source: DDNA_SIGNING_MODEL.md §"Complete Envelope Example" lines 330-353
 */
function createHeader(payload, vectorId) {
  return {
    ddna_version: '1.1',
    created_at: '2026-04-22T00:00:00Z',
    edm_version: '0.8.0',
    owner_user_id: payload.meta.owner_user_id,
    exportability: 'allowed',
    jurisdiction: payload.governance?.jurisdiction || 'AU',
    retention_policy: payload.governance?.retention_policy || {
      basis: 'user_defined',
      ttl_days: null,
      on_expiry: 'soft_delete',
    },
    consent_basis: payload.meta.consent_basis,
    masking_rules: [],
    payload_type: `edm.v0.8.0`,
    audit_chain: [
      {
        at: '2026-04-22T00:00:00Z',
        event: 'created',
        agent: 'test-vector-generator',
      },
    ],
  };
}

// =============================================================================
// VECTOR GENERATORS
// =============================================================================

const CREATED_TIMESTAMP = '2026-04-22T00:00:00Z';

function generateValidDidKeyEssential() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '001');
  const document = { ddna_header: header, edm_payload: payload };
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  return {
    id: '001-valid-did-key-essential',
    envelope: { ...document, proof },
    expected: {
      verified: true,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: null,
    },
    description: `# 001-valid-did-key-essential

## What This Vector Tests

Valid Ed25519 signature using did:key, essential profile, well-formed envelope.

This is the baseline "happy path" test case. A conforming verifier MUST return
\`verified: true\` for this envelope.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 7: Result = VALID
- DDNA_SIGNING_MODEL.md §"Conformance Requirements" MUST items 1-8

## Expected Result

\`\`\`json
{
  "verified": true,
  "verificationMethod": "${publicKeyToDid(TEST_KEY_1.publicKey)}",
  "created": "${CREATED_TIMESTAMP}"
}
\`\`\`
`,
  };
}

function generateValidDidKeyFull() {
  const payload = createFullPayload();
  const header = createHeader(payload, '002');
  const document = { ddna_header: header, edm_payload: payload };
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  return {
    id: '002-valid-did-key-full',
    envelope: { ...document, proof },
    expected: {
      verified: true,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: null,
    },
    description: `# 002-valid-did-key-full

## What This Vector Tests

Valid Ed25519 signature using did:key, full profile with all domains populated.

Tests that verification works correctly with larger, more complex payloads
including milky_way, gravity, impulse, system, and crosswalks domains.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 7: Result = VALID
- DDNA_SIGNING_MODEL.md §"Signing Input Construction": document = ddna_header + edm_payload

## Expected Result

\`\`\`json
{
  "verified": true,
  "verificationMethod": "${publicKeyToDid(TEST_KEY_1.publicKey)}",
  "created": "${CREATED_TIMESTAMP}"
}
\`\`\`
`,
  };
}

function generateValidPartnerJournaling() {
  const payload = createPartnerJournalingPayload();
  const header = createHeader(payload, '003');
  const document = { ddna_header: header, edm_payload: payload };
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  return {
    id: '003-valid-did-key-partner-journaling',
    envelope: { ...document, proof },
    expected: {
      verified: true,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: null,
    },
    description: `# 003-valid-did-key-partner-journaling

## What This Vector Tests

Valid signature with partner:com.deepadata.journaling.v1 profile.

Tests that partner: prefix profiles verify cleanly. The profile field is
part of edm_payload.meta and is covered by the signature.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 7: Result = VALID
- EDM spec: partner profiles use "partner:<reverse-domain>" format

## Expected Result

\`\`\`json
{
  "verified": true,
  "verificationMethod": "${publicKeyToDid(TEST_KEY_1.publicKey)}",
  "created": "${CREATED_TIMESTAMP}"
}
\`\`\`
`,
  };
}

function generateTamperedPayload() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '004');
  const document = { ddna_header: header, edm_payload: payload };
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  // Tamper with the payload AFTER signing
  const tamperedPayload = { ...payload };
  tamperedPayload.core = { ...tamperedPayload.core, anchor: 'TAMPERED VALUE' };

  return {
    id: '004-tampered-payload',
    envelope: { ddna_header: header, edm_payload: tamperedPayload, proof },
    expected: {
      verified: false,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: 'INVALID_SIGNATURE',
    },
    description: `# 004-tampered-payload

## What This Vector Tests

Valid signature, but edm_payload modified after sealing.

The envelope was signed correctly, then \`edm_payload.core.anchor\` was changed
from "test anchor" to "TAMPERED VALUE". This changes the document hash,
causing signature verification to fail.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 4:
  "Reconstruct the exact signing input"
- DDNA_SIGNING_MODEL.md §7 Step 6: Ed25519_Verify returns false
- DDNA_SIGNING_MODEL.md §7 Step 7: Result = INVALID

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "INVALID_SIGNATURE"
}
\`\`\`

The reconstructed signing input will differ from what was originally signed
because the document hash changes when the payload is modified.
`,
  };
}

function generateTamperedHeader() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '005');
  const document = { ddna_header: header, edm_payload: payload };
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  // Tamper with the header AFTER signing
  const tamperedHeader = { ...header, jurisdiction: 'TAMPERED' };

  return {
    id: '005-tampered-header',
    envelope: { ddna_header: tamperedHeader, edm_payload: payload, proof },
    expected: {
      verified: false,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: 'INVALID_SIGNATURE',
    },
    description: `# 005-tampered-header

## What This Vector Tests

Valid signature, but ddna_header modified after sealing.

The envelope was signed correctly, then \`ddna_header.jurisdiction\` was changed
from "AU" to "TAMPERED". This changes the document hash, causing signature
verification to fail.

## Spec References

- DDNA_SIGNING_MODEL.md §"Signing Input Construction" Step 2:
  "Create the document object containing the envelope data to be signed"
- DDNA_SIGNING_MODEL.md §7 Step 4: Reconstruct signing input includes ddna_header
- DDNA_SIGNING_MODEL.md §7 Step 7: Result = INVALID

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "INVALID_SIGNATURE"
}
\`\`\`

The ddna_header is part of the signed document, so any modification
invalidates the signature.
`,
  };
}

function generateWrongPublicKey() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '006');
  const document = { ddna_header: header, edm_payload: payload };

  // Sign with Key 1's private key, but claim Key 2's DID
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  // Replace the verificationMethod with Key 2's DID
  const wrongKeyProof = {
    ...proof,
    verificationMethod: publicKeyToDid(TEST_KEY_2.publicKey),
  };

  return {
    id: '006-wrong-public-key',
    envelope: { ...document, proof: wrongKeyProof },
    expected: {
      verified: false,
      verificationMethod: publicKeyToDid(TEST_KEY_2.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: 'INVALID_SIGNATURE',
    },
    description: `# 006-wrong-public-key

## What This Vector Tests

Signature created with Key A, but verificationMethod claims Key B.

The proofValue was created using Test Key 1's private key, but the
verificationMethod field points to Test Key 2's did:key. When the verifier
resolves Key 2 and attempts to verify, the signature check fails.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 3:
  "Resolve the DID URL to obtain the public key"
- DDNA_SIGNING_MODEL.md §7 Step 6:
  "valid = Ed25519_Verify(public_key, signing_input, signature)"
- The wrong public key means Ed25519_Verify returns false

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "INVALID_SIGNATURE"
}
\`\`\`

This tests key binding: the signature must match the claimed verificationMethod.
`,
  };
}

function generateMalformedProofValue() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '007');
  const document = { ddna_header: header, edm_payload: payload };
  const proof = createProof(TEST_KEY_1.privateKey, TEST_KEY_1.publicKey, document, CREATED_TIMESTAMP);

  // Replace proofValue with invalid base58btc (contains invalid characters)
  const malformedProof = {
    ...proof,
    proofValue: 'zINVALID!!!NOT_BASE58_@#$%',
  };

  return {
    id: '007-malformed-proof-value',
    envelope: { ...document, proof: malformedProof },
    expected: {
      verified: false,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: CREATED_TIMESTAMP,
      expectedReason: 'MALFORMED_PROOF_VALUE',
    },
    description: `# 007-malformed-proof-value

## What This Vector Tests

proofValue is not valid base58btc encoding.

The proofValue field contains characters that are not valid base58btc
(!, @, #, $, %). Decoding should fail before signature verification.

## Spec References

- DDNA_SIGNING_MODEL.md §"Proof Fields" line 104:
  "proofValue: Multibase-encoded signature (base58-btc, prefix 'z')"
- DDNA_SIGNING_MODEL.md §7 Step 5: "signature = multibase_decode(proof.proofValue)"
- Multibase spec: base58btc uses alphabet "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "MALFORMED_PROOF_VALUE"
}
\`\`\`

Implementations should detect invalid base58btc encoding and return
an appropriate error before attempting signature verification.
`,
  };
}

function generateMissingProof() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '008');

  // Envelope without proof block
  return {
    id: '008-missing-proof',
    envelope: { ddna_header: header, edm_payload: payload },
    expected: {
      verified: false,
      verificationMethod: null,
      created: null,
      expectedReason: 'MISSING_PROOF',
    },
    description: `# 008-missing-proof

## What This Vector Tests

Envelope has ddna_header and edm_payload but no proof block.

This represents an "unsealed" envelope that cannot be verified.

## Spec References

- DDNA_SIGNING_MODEL.md §"Unsealed Envelopes" lines 498-517:
  "Envelopes MAY exist without a proof block. An unsealed envelope...
   Cannot be verified for tampering"
- DDNA_SIGNING_MODEL.md §7 Step 1: "Extract... proof"
- deepadata-com/lib/ddna/verify.ts:47-49: throws "Invalid envelope: missing proof"

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "MISSING_PROOF"
}
\`\`\`

Implementations should detect the missing proof block early in validation.
`,
  };
}

function generateDidWebNoResolver() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '009');
  const document = { ddna_header: header, edm_payload: payload };

  // Create a proof with did:web (which requires external resolver)
  const proofOptions = {
    type: 'DataIntegrityProof',
    cryptosuite: 'eddsa-jcs-2022',
    created: CREATED_TIMESTAMP,
    verificationMethod: 'did:web:example.com#key-1',
    proofPurpose: 'assertionMethod',
  };

  const signingInput = constructSigningInput(proofOptions, document);
  const proofValue = sign(TEST_KEY_1.privateKey, signingInput);

  const proof = { ...proofOptions, proofValue };

  return {
    id: '009-did-web-no-resolver',
    envelope: { ...document, proof },
    expected: {
      verified: false,
      verificationMethod: 'did:web:example.com#key-1',
      created: CREATED_TIMESTAMP,
      expectedReason: 'DID_WEB_NO_RESOLVER',
    },
    description: `# 009-did-web-no-resolver

## What This Vector Tests

Valid signature structure, did:web verificationMethod, no resolver provided.

When using ddna-reader's verify() without a didResolver option, did:web
DIDs cannot be resolved (the library makes no HTTP calls by design).

## Spec References

- ADR-0020 §"did:web Resolution: Injected Resolver Pattern":
  "If didResolver not provided... did:web throws
   Error: did:web requires didResolver option"
- deepadata-ddna-reader/src/lib/verify.ts: resolveVerificationMethod throws
  for did:web without custom resolver

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "DID_WEB_NO_RESOLVER"
}
\`\`\`

This tests the injected resolver pattern. Callers must provide their own
resolver for did:web. The library stays offline-capable by default.
`,
  };
}

function generateExpiredProof() {
  const payload = createEssentialPayload();
  const header = createHeader(payload, '010');
  const document = { ddna_header: header, edm_payload: payload };

  // Create a proof that expires in the past
  const proof = createProof(
    TEST_KEY_1.privateKey,
    TEST_KEY_1.publicKey,
    document,
    '2020-01-01T00:00:00Z', // created in 2020
    { expires: '2020-01-02T00:00:00Z' } // expired in 2020
  );

  return {
    id: '010-expired-proof',
    envelope: { ...document, proof },
    expected: {
      verified: false,
      verificationMethod: publicKeyToDid(TEST_KEY_1.publicKey),
      created: '2020-01-01T00:00:00Z',
      expectedReason: 'PROOF_EXPIRED',
    },
    description: `# 010-expired-proof

## What This Vector Tests

Valid signature, but proof.expires is in the past.

The proof has an expires field set to 2020-01-02T00:00:00Z, which is
in the past relative to any reasonable verification time.

## Spec References

- DDNA_SIGNING_MODEL.md §"Optional Proof Fields":
  "expires: ISO 8601 timestamp when proof expires"
- DDNA_SIGNING_MODEL.md §"Timestamp Validation":
  "Verifiers SHOULD check... expires (if present) has not passed"
- deepadata-com/lib/ddna/verify.ts:171-181: checks expires against now

## Expected Result

\`\`\`json
{
  "verified": false,
  "expectedReason": "PROOF_EXPIRED"
}
\`\`\`

**Note:** Implementations running with skipTimestampCheck=true will not
catch this error. The test should be run with timestamp checking enabled.
`,
  };
}

// =============================================================================
// MAIN
// =============================================================================

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
  }
  return bytes;
}

function writeVector(vector) {
  const vectorDir = path.join(VECTORS_DIR, vector.id);
  fs.mkdirSync(vectorDir, { recursive: true });

  fs.writeFileSync(
    path.join(vectorDir, 'envelope.ddna'),
    JSON.stringify(vector.envelope, null, 2)
  );

  fs.writeFileSync(
    path.join(vectorDir, 'expected.json'),
    JSON.stringify(vector.expected, null, 2)
  );

  fs.writeFileSync(
    path.join(vectorDir, 'description.md'),
    vector.description
  );

  console.log(`Generated: ${vector.id}`);
}

function writeIndex(vectors) {
  const index = {
    version: '1.0.0',
    spec_version: '0.8.0',
    ddna_version: '1.1',
    generated_at: new Date().toISOString(),
    test_keys: {
      key_1: {
        did: publicKeyToDid(TEST_KEY_1.publicKey),
        public_key_hex: bytesToHex(TEST_KEY_1.publicKey),
        source: 'RFC 8032 §7.1 Test 1',
      },
      key_2: {
        did: publicKeyToDid(TEST_KEY_2.publicKey),
        public_key_hex: bytesToHex(TEST_KEY_2.publicKey),
        source: 'RFC 8032 §7.1 Test 2',
      },
    },
    vectors: vectors.map(v => ({
      id: v.id,
      expected_verified: v.expected.verified,
      tests: getVectorSummary(v.id),
      spec_reference: getSpecReference(v.id),
    })),
  };

  fs.writeFileSync(
    path.join(VECTORS_DIR, 'INDEX.json'),
    JSON.stringify(index, null, 2)
  );

  console.log(`\nGenerated INDEX.json with ${vectors.length} vectors`);
}

function bytesToHex(bytes) {
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

function getVectorSummary(id) {
  const summaries = {
    '001-valid-did-key-essential': 'valid signature, did:key, essential profile',
    '002-valid-did-key-full': 'valid signature, did:key, full profile',
    '003-valid-did-key-partner-journaling': 'valid signature, partner: profile',
    '004-tampered-payload': 'payload modified after signing',
    '005-tampered-header': 'header modified after signing',
    '006-wrong-public-key': 'signature from different key than claimed',
    '007-malformed-proof-value': 'invalid base58btc in proofValue',
    '008-missing-proof': 'envelope without proof block',
    '009-did-web-no-resolver': 'did:web without injected resolver',
    '010-expired-proof': 'proof.expires in the past',
  };
  return summaries[id] || '';
}

function getSpecReference(id) {
  const refs = {
    '001-valid-did-key-essential': 'DDNA_SIGNING_MODEL.md §7',
    '002-valid-did-key-full': 'DDNA_SIGNING_MODEL.md §7',
    '003-valid-did-key-partner-journaling': 'DDNA_SIGNING_MODEL.md §7',
    '004-tampered-payload': 'DDNA_SIGNING_MODEL.md §7 Step 4, Step 6',
    '005-tampered-header': 'DDNA_SIGNING_MODEL.md §7 Step 4, Step 6',
    '006-wrong-public-key': 'DDNA_SIGNING_MODEL.md §7 Step 3, Step 6',
    '007-malformed-proof-value': 'DDNA_SIGNING_MODEL.md §7 Step 5',
    '008-missing-proof': 'DDNA_SIGNING_MODEL.md §"Unsealed Envelopes"',
    '009-did-web-no-resolver': 'ADR-0020 §"did:web Resolution"',
    '010-expired-proof': 'DDNA_SIGNING_MODEL.md §"Timestamp Validation"',
  };
  return refs[id] || '';
}

async function main() {
  console.log('Generating .ddna verification test vectors...\n');
  console.log('Test Key 1 DID:', publicKeyToDid(TEST_KEY_1.publicKey));
  console.log('Test Key 2 DID:', publicKeyToDid(TEST_KEY_2.publicKey));
  console.log('');

  const vectors = [
    generateValidDidKeyEssential(),
    generateValidDidKeyFull(),
    generateValidPartnerJournaling(),
    generateTamperedPayload(),
    generateTamperedHeader(),
    generateWrongPublicKey(),
    generateMalformedProofValue(),
    generateMissingProof(),
    generateDidWebNoResolver(),
    generateExpiredProof(),
  ];

  for (const vector of vectors) {
    writeVector(vector);
  }

  writeIndex(vectors);

  console.log('\nDone! Generated 10 test vectors.');
}

main().catch(console.error);
