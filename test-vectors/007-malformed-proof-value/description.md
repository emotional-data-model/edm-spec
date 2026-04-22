# 007-malformed-proof-value

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

```json
{
  "verified": false,
  "expectedReason": "MALFORMED_PROOF_VALUE"
}
```

Implementations should detect invalid base58btc encoding and return
an appropriate error before attempting signature verification.
