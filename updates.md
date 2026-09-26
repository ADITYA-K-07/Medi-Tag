# MediTag Build Progress

Last updated: 2026-09-26

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

- Most recently completed: Session 1 of 19 - repository foundation
- Overall status: Session 1 complete; Session 2 not started
- Next milestone: database models, migrations, encryption, and Ed25519 primitives

## Completed sessions

### Session 1 - Repository foundation (2026-09-26)

- Commit: pending final Session 1 commit
- Created the Flutter Android, Next.js, and FastAPI application foundations.
- Added local PostgreSQL/Redis Compose configuration and environment examples.
- Added baseline tests, linting, production build checks, and GitHub Actions CI.
- Recorded the core architecture decisions and shared-contract ownership.
- Replaced generated demo screens with small MediTag foundation screens.
- Expanded the root and application READMEs with direct setup commands.

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
- No domain schemas or database migrations exist yet; they belong to Session 2.

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

## Remaining session checklist

- [x] Session 1 - Repository foundation and this progress file
- [ ] Session 2 - Database models, migrations, encryption, and Ed25519
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
- Web: `NEXT_PUBLIC_API_URL`

## Next session starting instructions

1. Read this file and `docs/adr` before changing code.
2. Run the Session 1 checks to establish a clean baseline.
3. Add SQLAlchemy, psycopg, Alembic, settings, and cryptography dependencies to
   `services/api/pyproject.toml`.
4. Design only the agreed Session 2 tables and generate the initial migration.
5. Add field-encryption and Ed25519 utilities after the migration passes against
   PostgreSQL; keep their interfaces small and cover them with fixed test vectors.
