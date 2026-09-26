# MediTag

MediTag is an NFC-based emergency medical information system. This repository
contains the Android app, web app, backend API, and local development services.

The project is being built in small, tested sessions. Read [updates.md](updates.md)
first when starting work; it records what is complete and what should happen
next.

## Repository layout

```text
apps/
  mobile/          Flutter Android application
  web/             Next.js website and administration UI
services/
  api/             FastAPI backend
packages/
  contracts/       Shared API and NFC format documentation
infra/
  compose.yaml     Local PostgreSQL and Redis services
docs/
  adr/             Short architecture decision records
```

The structure intentionally stays conventional and shallow. Add a new folder
only when it owns a clear responsibility.

## Prerequisites

- Flutter 3.41 or a compatible stable release with the Android toolchain
- Python 3.11 or newer
- Node.js 20.9 or newer and npm
- Docker Desktop with Docker Compose (for PostgreSQL and Redis)

## First-time setup

Copy each example environment file before running a service. Do not commit the
real files.

```powershell
Copy-Item .env.example .env
Copy-Item services/api/.env.example services/api/.env
Copy-Item apps/web/.env.example apps/web/.env.local
```

Start local infrastructure:

```powershell
docker compose --env-file .env -f infra/compose.yaml up -d
```

Start the API:

```powershell
cd services/api
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Start the website:

```powershell
cd apps/web
npm install
npm run dev
```

Run the Android app:

```powershell
cd apps/mobile
flutter pub get
flutter run
```

## Verification

```powershell
cd services/api
python -m pytest
python -m ruff check --no-cache .
python -m alembic upgrade head --sql

cd ../../apps/web
npm test
npm run lint
npm run build

cd ../mobile
flutter analyze
flutter test
```

The API health endpoints are `GET /health` and `GET /ready`.

For implementation context, see the short decisions in `docs/adr`, the
[database map](docs/database.md), and the NFC contract in
`packages/contracts/nfc-payload-v1.md`.

## Safety

This foundation is not ready for real medical information. Use synthetic test
data until the later privacy, security, encryption, auditing, and pilot review
sessions are complete.
