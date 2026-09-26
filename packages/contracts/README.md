# Shared contracts

FastAPI's generated OpenAPI document will be the source of truth for HTTP
request and response shapes. Later sessions will generate the Dart and
TypeScript clients from that document.

This package will also hold language-neutral NFC format test vectors so the
backend and Flutter app sign and verify exactly the same bytes.

No application code belongs here unless it is generated or genuinely shared as
a contract.
