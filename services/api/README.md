# MediTag API

The API is intentionally small in Session 1. Run it from this directory after
installing the development dependencies:

```powershell
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated OpenAPI interface.
