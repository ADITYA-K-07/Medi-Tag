# MediTag API

The API is intentionally small in Session 1. Run it from this directory after
installing the development dependencies:

```powershell
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated OpenAPI interface.

## Database migrations

Apply migrations after configuring `DATABASE_URL`:

```powershell
python -m alembic upgrade head
```

Validate the PostgreSQL SQL without connecting to a database:

```powershell
python -m alembic upgrade head --sql
```

Sensitive emergency profiles and medical-record payloads are encrypted before
storage. Generate and store field-encryption and Ed25519 signing keys outside
the repository; `.env.example` contains only the required variable names.

For local development, generate fresh values and copy them into the untracked
`.env` file:

```powershell
python scripts/generate_dev_keys.py
```
