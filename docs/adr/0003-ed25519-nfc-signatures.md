# ADR 0003: Sign NFC snapshots with Ed25519

Status: accepted

The backend holds the Ed25519 private key and the mobile app contains only public
verification keys. This lets the app authenticate an offline snapshot without
shipping a shared HMAC secret that could be extracted and used to forge tags.

The signature proves who created a snapshot, not whether it was later revoked.
Offline screens must state that current status was not checked.
