# 005-tampered-header

## What This Vector Tests

Valid signature, but ddna_header modified after sealing.

The envelope was signed correctly, then `ddna_header.jurisdiction` was changed
from "AU" to "TAMPERED". This changes the document hash, causing signature
verification to fail.

## Spec References

- DDNA_SIGNING_MODEL.md §"Signing Input Construction" Step 2:
  "Create the document object containing the envelope data to be signed"
- DDNA_SIGNING_MODEL.md §7 Step 4: Reconstruct signing input includes ddna_header
- DDNA_SIGNING_MODEL.md §7 Step 7: Result = INVALID

## Expected Result

```json
{
  "verified": false,
  "expectedReason": "INVALID_SIGNATURE"
}
```

The ddna_header is part of the signed document, so any modification
invalidates the signature.
