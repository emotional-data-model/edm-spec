# 002-valid-did-key-full

## What This Vector Tests

Valid Ed25519 signature using did:key, full profile with all domains populated.

Tests that verification works correctly with larger, more complex payloads
including milky_way, gravity, impulse, system, and crosswalks domains.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 7: Result = VALID
- DDNA_SIGNING_MODEL.md §"Signing Input Construction": document = ddna_header + edm_payload

## Expected Result

```json
{
  "verified": true,
  "verificationMethod": "did:key:z6MktwupdmLXVVqTzCw4i46r4uGyosGXRnR3XjN4Zq7oMMsw",
  "created": "2026-04-22T00:00:00Z"
}
```
