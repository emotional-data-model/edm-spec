# .ddna Verification Test Vectors

Canonical test vectors for .ddna envelope verification per ADR-0020.

## Purpose

These test vectors serve as the **source of truth** for verification correctness.
Any conforming reader implementation must produce the documented expected results
when run against these vectors.

Per ADR-0020:
> "Test vectors in edm-spec are the canonical source of truth for verification correctness"

## Format

Each test vector is a self-contained directory:

```
test-vectors/
├── README.md                          # This file
├── INDEX.json                         # Manifest of all vectors
├── scripts/
│   └── generate-vectors.mjs           # Generation script (Path B)
├── 001-valid-did-key-essential/
│   ├── envelope.ddna                  # The test envelope
│   ├── expected.json                  # Expected verify result
│   └── description.md                 # What this vector tests
├── 002-valid-did-key-full/
│   └── ...
└── ...
```

### envelope.ddna

A complete .ddna envelope with `ddna_header`, `edm_payload`, and `proof` blocks.

### expected.json

```json
{
  "verified": true,
  "verificationMethod": "did:key:z6Mk...",
  "created": "2026-04-22T00:00:00Z",
  "expectedReason": null
}
```

For invalid vectors:
```json
{
  "verified": false,
  "verificationMethod": "did:key:z6Mk...",
  "created": "2026-04-22T00:00:00Z",
  "expectedReason": "INVALID_SIGNATURE"
}
```

### description.md

Human-readable description of what the vector tests, with citations to spec sections.

## How Conforming Readers Should Consume Vectors

```typescript
import { verify } from 'ddna-reader';
import { readFileSync } from 'fs';

const index = JSON.parse(readFileSync('test-vectors/INDEX.json', 'utf-8'));

for (const vector of index.vectors) {
  const envelope = JSON.parse(
    readFileSync(`test-vectors/${vector.id}/envelope.ddna`, 'utf-8')
  );
  const expected = JSON.parse(
    readFileSync(`test-vectors/${vector.id}/expected.json`, 'utf-8')
  );

  // Skip timestamp checks for deterministic test results
  const result = await verify(envelope, { skipTimestampCheck: true });

  assert(result.valid === expected.verified);
  if (!expected.verified) {
    // Verify reason category matches (implementation-specific wording allowed)
    assert(matchesReasonCategory(result.reason, expected.expectedReason));
  }
}
```

## Test Keys

**WARNING: These are test fixtures, NOT production keys.**

The test vectors use deterministic keys generated from fixed seeds. These keys
are committed to the repository for reproducibility. They MUST NOT be used in
any production context.

### Test Key 1 (Primary)

```
Private Key (hex): 9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60
Public Key (hex):  d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a
DID: did:key:z6MkiTBz1ymuepAQ4HEHYSF1H8quG5GLVVQR3djdX3mDooWp
```

Source: Ed25519 test vector from RFC 8032 §7.1 (Test 1)

### Test Key 2 (For wrong-key test)

```
Private Key (hex): 4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb
Public Key (hex):  3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c
DID: did:key:z6MknGc3ocHs3zdPiJbnaaqDi5eMTtVJdnFT8bihzMBhMdYZ
```

Source: Ed25519 test vector from RFC 8032 §7.1 (Test 2)

## Reason Category Vocabulary

These categories provide controlled vocabulary for expected error reasons.
Implementation-specific error messages should map to these categories.

| Category | Description | Spec Reference |
|----------|-------------|----------------|
| `VALID` | Signature verified successfully | DDNA_SIGNING_MODEL.md §7 Step 7 |
| `INVALID_SIGNATURE` | Ed25519 signature verification failed | DDNA_SIGNING_MODEL.md §7 Step 6 |
| `MISSING_PROOF` | Envelope has no proof block | DDNA_SIGNING_MODEL.md §7 Step 1 |
| `MALFORMED_PROOF_VALUE` | proofValue is not valid base58btc | DDNA_SIGNING_MODEL.md §7 Step 5, §4 |
| `INVALID_PROOF_STRUCTURE` | Required proof field missing or invalid | DDNA_SIGNING_MODEL.md §7 Step 2 |
| `DID_RESOLUTION_FAILED` | Could not resolve verificationMethod | DDNA_SIGNING_MODEL.md §7 Step 3 |
| `DID_WEB_NO_RESOLVER` | did:web without injected resolver | ADR-0020 §"did:web Resolution" |
| `PROOF_EXPIRED` | proof.expires is in the past | DDNA_SIGNING_MODEL.md §"Timestamp Validation" |
| `PROOF_FUTURE` | proof.created is in the future | DDNA_SIGNING_MODEL.md §"Timestamp Validation" |

## Versioning Policy

Test vectors are versioned alongside the spec:

- `spec_version` in INDEX.json indicates which EDM version the payloads conform to
- `ddna_version` indicates the envelope format version
- Test vector changes require a new `version` in INDEX.json

Adding new vectors: increment patch version (1.0.0 → 1.0.1)
Modifying existing vectors: increment minor version (1.0.0 → 1.1.0)
Breaking changes: increment major version (1.0.0 → 2.0.0)

## How to Regenerate Vectors

Vectors are generated using `scripts/generate-vectors.mjs`:

```bash
cd test-vectors
node scripts/generate-vectors.mjs
```

The script uses deterministic test keys and fixed timestamps for reproducibility.
Running the script should produce byte-identical output.

## References

- [ADR-0020: Open Verification in ddna-reader](../../../deepadata-com/internal_document_series/ADR/ADR-0020-open-verification-in-ddna-reader.md)
- [DDNA_SIGNING_MODEL.md](../docs/DDNA_SIGNING_MODEL.md)
- [RFC 8032 §7.1: Ed25519 Test Vectors](https://www.rfc-editor.org/rfc/rfc8032#section-7.1)
- [RFC 8785: JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785)
