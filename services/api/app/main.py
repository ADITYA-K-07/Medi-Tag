from fastapi import FastAPI

app = FastAPI(title="MediTag API", version="0.1.0")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Report whether the API process is running."""
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    """Report whether required dependencies are ready.

    Database and Redis checks will be added when those integrations are created.
    """
    return {"status": "ready"}
