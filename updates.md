# MediTag Build Progress

Last updated: 2026-09-26 after Session 2

## Project objective

Build a readable, maintainable NFC medical information platform consisting of
one role-based Flutter Android APK, a FastAPI/PostgreSQL backend, and a Next.js
website. NTAG216 tags will expose the explicitly public emergency fields while
Tier 2 medical information remains restricted to citizens and verified doctors.

## Locked architecture decisions

- One Android Flutter application for public, citizen, and doctor flows.
- FastAPI is the only backend and PostgreSQL is the source of truth.
- Next.js provides the public tag page, dashboards, and administration UI.
- NTAG216 tags contain an HTTPS URI and a value-only text record.
- Public values are name, emergency number, blood group, allergies, and critical
  conditions.
- Ed25519 signatures enable offline authenticity checks without shipping a
  signing secret in the APK.
- A citizen may have at most three active or pending tags.
- Doctor access requires NMC/SMC verification with an admin-review fallback.
- Real medical data is prohibited until the pilot security and privacy gates
  pass.
- Code should remain conventional, shallow, and easy to modify.

## Current session and overall status

- Most recently completed: Session 2 of 19 - data and cryptography foundation
- Overall status: Session 2 complete; Session 3 not started
- Next milestone: citizen authentication and account recovery

## Completed sessions

### Session 1 - Repository foundation (2026-09-26)

- Implementation commit: `63d8c9e` (`chore: bootstrap MediTag monorepo`)
- Created the Flutter Android, Next.js, and FastAPI application foundations.
- Added local PostgreSQL/Redis Compose configuration and environment examples.
- Added baseline tests, linting, production build checks, and GitHub Actions CI.
- Recorded the core architecture decisions and shared-contract ownership.
- Replaced generated demo screens with small MediTag foundation screens.
- Expanded the root and application READMEs with direct setup commands.

### Session 2 - Database and cryptography (2026-09-26)

- Implementation commit: `52b8030` (`feat: add data and cryptography foundation`)
- Added the account-centered SQLAlchemy schema and initial Alembic migration.
- Added versioned Fernet field encryption with authenticated decryption.
- Added deterministic Ed25519 tag signing and public-key verification.
- Published the NFC version 1 canonical byte format and fixed test vector.
- Added environment-backed settings and a safe local key-generation script.
- Configured CI to apply, downgrade, and reapply the migration on PostgreSQL 17.
- Added a concise database map for future sessions and manual maintenance.

## Current repository structure

```text
apps/mobile        Flutter Android app
apps/web           Next.js web app
services/api       FastAPI service
packages/contracts Shared contract documentation
infra              Local service configuration
docs/adr           Architecture decisions
```

## Implemented APIs, schemas, and migrations

- `GET /health`: process health response.
- `GET /ready`: dependency-readiness placeholder.
- No authentication or domain endpoints exist yet; Session 3 starts those APIs.
- Migration `20260926_01` creates `accounts`, role profiles, doctor verification
  events, consent history, encrypted emergency profiles and medical records,
  NFC tags/write versions, refresh sessions, one-time tokens, and access logs.
- Sensitive payloads store ciphertext beside an explicit encryption-key version.
- NFC signatures use the canonical contract in
  `packages/contracts/nfc-payload-v1.md`.

## Verification commands and latest results

Session 1 results:

- `flutter analyze`: passed, no issues
- `flutter test`: passed, 1 test
- `python -m ruff check --no-cache .`: passed
- `python -m pytest -p no:cacheprovider`: passed, 2 tests
- Live `GET /health` and `GET /ready`: passed with HTTP 200
- `npm test`: passed, 1 test
- `npm run lint`: passed
- `npm run build`: passed with Next.js 16.3.6
- Compose YAML parse and expected-service check: passed
- `docker compose config`: not run because Docker is not installed
- `git diff --check`: passed apart from Git's informational LF/CRLF warning

Session 2 results:

- Backend Ruff: passed
- Backend pytest: passed, 15 tests
- Alembic offline upgrade: passed and emitted all 13 tables
- Alembic offline downgrade: passed in reverse dependency order
- Migration output contains no duplicate SQL terminators
- Local key generator: passed and emitted the five expected variable names
- Flutter regression: analysis passed and 1 test passed
- Web regression: test, lint, and Next.js production build passed
- Live PostgreSQL migration: not run locally because Docker/PostgreSQL is absent;
  PostgreSQL 17 upgrade/downgrade/re-upgrade validation is configured in CI

## Remaining session checklist

- [x] Session 1 - Repository foundation and this progress file
- [x] Session 2 - Database models, migrations, encryption, and Ed25519
- [ ] Session 3 - Citizen authentication and recovery
- [ ] Session 4 - Citizen profiles, records, consent, export, and deletion
- [ ] Session 5 - NFC tag lifecycle, signatures, and public scans
- [ ] Session 6 - Doctor authentication, registry verification, and admin review
- [ ] Session 7 - Doctor access, notes, auditing, and backend hardening
- [ ] Session 8 - Physical NTAG216 feasibility tests
- [ ] Session 9 - Flutter architecture, authentication, and role routing
- [ ] Session 10 - Flutter citizen profile and record flows
- [ ] Session 11 - Flutter NFC writing and tag management
- [ ] Session 12 - Flutter public/offline scanning
- [ ] Session 13 - Flutter doctor workflow
- [ ] Session 14 - Flutter stabilization and internal APK
- [ ] Session 15 - Website public experience and authentication
- [ ] Session 16 - Citizen and doctor web dashboards
- [ ] Session 17 - Doctor-verification admin portal
- [ ] Session 18 - Deployment and operations
- [ ] Session 19 - End-to-end validation and signed release

## Known defects, blockers, and external dependencies

- Docker is not currently available on this workstation, so the Compose file
  cannot yet be validated or the local services started.
- NMC/SMC integration access, the production domain, hosting accounts, email
  service, object storage, and signing material will be needed in later sessions.
- Do not store any secret value or patient information in this file.

## Required environment variable names

- Root: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`,
  `REDIS_PORT`
- API: `APP_ENV`, `API_HOST`, `API_PORT`, `DATABASE_URL`, `REDIS_URL`
- API cryptography: `FIELD_ENCRYPTION_CURRENT_VERSION`,
  `FIELD_ENCRYPTION_KEYS`, `TAG_SIGNING_KEY_ID`, `TAG_SIGNING_PRIVATE_KEY`,
  `TAG_SIGNING_PUBLIC_KEYS`
- Web: `NEXT_PUBLIC_API_URL`

## Next session starting instructions

1. Read this file, `docs/database.md`, and the Session 2 security modules.
2. Run Ruff, pytest, and the offline Alembic upgrade as the baseline.
3. Add password hashing, access JWT, refresh-token, and email-token services.
4. Add the database session dependency without creating an engine at import time.
5. Implement citizen register, email verification, login, refresh, logout,
   forgot-password, and reset-password endpoints behind a small auth service.
6. Use a console email adapter in development and keep provider delivery behind
   one interface for the deployment session.
7. Test duplicate email, unverified login, rotation/reuse, expiry, revocation,
   invalid reset tokens, and account isolation before completing Session 3.
