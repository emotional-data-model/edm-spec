# 008-missing-proof

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

```json
{
  "verified": false,
  "expectedReason": "MISSING_PROOF"
}
```

Implementations should detect the missing proof block early in validation.
