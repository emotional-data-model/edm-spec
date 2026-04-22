# 010-expired-proof

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

```json
{
  "verified": false,
  "expectedReason": "PROOF_EXPIRED"
}
```

**Note:** Implementations running with skipTimestampCheck=true will not
catch this error. The test should be run with timestamp checking enabled.
