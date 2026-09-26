# NFC payload version 1

An NTAG216 contains two NDEF records in this order:

1. An HTTPS URI with the public tag UUID and signature parameters.
2. A UTF-8 text record containing five value-only lines.

The text lines are full name, primary emergency phone, blood group, allergies,
and critical conditions. Lists use semicolons and an absent value is `-`.

## Signed message

Ed25519 signs this exact byte sequence:

```text
"MTG1\0"                     5-byte format marker
tag UUID                     16 raw bytes
write counter                unsigned 32-bit big-endian
profile revision             unsigned 32-bit big-endian
issued-at Unix timestamp     unsigned 64-bit big-endian
SHA-256(public text)         32 bytes
```

Before hashing, text is normalized to Unicode NFC and all line endings become
LF. Signatures and raw keys use unpadded Base64 URL encoding.

The test vector in `services/api/tests/test_nfc_signing.py` is normative for all
backend and Flutter implementations.
