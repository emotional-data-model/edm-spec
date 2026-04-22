# 003-valid-did-key-partner-journaling

## What This Vector Tests

Valid signature with partner:com.deepadata.journaling.v1 profile.

Tests that partner: prefix profiles verify cleanly. The profile field is
part of edm_payload.meta and is covered by the signature.

## Spec References

- DDNA_SIGNING_MODEL.md §7 "Verification Procedure" Step 7: Result = VALID
- EDM spec: partner profiles use "partner:<reverse-domain>" format

## Expected Result

```json
{
  "verified": true,
  "verificationMethod": "did:key:z6MktwupdmLXVVqTzCw4i46r4uGyosGXRnR3XjN4Zq7oMMsw",
  "created": "2026-04-22T00:00:00Z"
}
```
