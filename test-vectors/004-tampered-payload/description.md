# 004-tampered-payload

## What This Vector Tests

Valid signature, but edm_payload modified after sealing.

The envelope was signed correctly, then `edm_payload.core.anchor` was changed
from "test anchor" to "TAMPERED VALUE". This changes the document hash,
causing signature verification to fail.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 4:
  "Reconstruct the exact signing input"
- DDNA_SIGNING_MODEL.md §7 Step 6: Ed25519_Verify returns false
- DDNA_SIGNING_MODEL.md §7 Step 7: Result = INVALID

## Expected Result

```json
{
  "verified": false,
  "expectedReason": "INVALID_SIGNATURE"
}
```

The reconstructed signing input will differ from what was originally signed
because the document hash changes when the payload is modified.
