# 006-wrong-public-key

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

```json
{
  "verified": false,
  "expectedReason": "INVALID_SIGNATURE"
}
```

This tests key binding: the signature must match the claimed verificationMethod.
