# 009-did-web-no-resolver

## What This Vector Tests

Valid signature structure, did:web verificationMethod, no resolver provided.

When using ddna-reader's verify() without a didResolver option, did:web
DIDs cannot be resolved (the library makes no HTTP calls by design).

## Spec References

- ADR-0020 §"did:web Resolution: Injected Resolver Pattern":
  "If didResolver not provided... did:web throws
   Error: did:web requires didResolver option"
- deepadata-ddna-reader/src/lib/verify.ts: resolveVerificationMethod throws
  for did:web without custom resolver

## Expected Result

```json
{
  "verified": false,
  "expectedReason": "DID_WEB_NO_RESOLVER"
}
```

This tests the injected resolver pattern. Callers must provide their own
resolver for did:web. The library stays offline-capable by default.
