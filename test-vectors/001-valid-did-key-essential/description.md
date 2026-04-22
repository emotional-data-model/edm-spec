# 001-valid-did-key-essential

## What This Vector Tests

Valid Ed25519 signature using did:key, essential profile, well-formed envelope.

This is the baseline "happy path" test case. A conforming verifier MUST return
`verified: true` for this envelope.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 7: Result = VALID
- DDNA_SIGNING_MODEL.md §"Conformance Requirements" MUST items 1-8

## Expected Result

```json
{
  "verified": true,
  "verificationMethod": "did:key:z6MktwupdmLXVVqTzCw4i46r4uGyosGXRnR3XjN4Zq7oMMsw",
  "created": "2026-04-22T00:00:00Z"
}
```
