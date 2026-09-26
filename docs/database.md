# Database map

The SQLAlchemy definitions live in `services/api/app/models.py`. The first
Alembic migration is `20260926_01_initial_schema.py`.

## Identity and access

- `accounts` stores shared login identity for citizens, doctors, and admins.
- `citizens`, `doctors`, and `admins` store role-specific profile fields.
- `refresh_sessions` stores only hashes of refresh tokens.
- `one_time_tokens` stores only hashes of email-verification and password-reset
  tokens.

## Medical information

- `emergency_profiles` stores one versioned encrypted JSON payload per citizen.
- `medical_records` stores versioned encrypted record payloads.
- `consent_records` is an append-only history of consent decisions.

The ciphertext and its `key_version` always travel together. The encryption key
is an environment secret and is never stored in PostgreSQL.

## NFC tags

- `nfc_tags` owns the physical tag identity and current write counter.
- `tag_write_versions` records every server-signed payload offered for writing.

The limit of three active or pending tags is enforced transactionally in the
service layer because it is a count rule rather than a row-level constraint.

## Verification and auditing

- `doctor_verification_events` records registry and administrator decisions.
- `access_logs` records allowed and denied data access without storing medical
  content in the log.

Foreign keys cascade when owned data has no independent purpose. Audit records
use `ON DELETE SET NULL` where retaining a non-identifying event remains useful.
