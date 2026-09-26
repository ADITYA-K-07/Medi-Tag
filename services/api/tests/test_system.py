import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def get(path: str):
    async def request():
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            return await client.get(path)

    return asyncio.run(request())


def test_health() -> None:
    response = get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready() -> None:
    response = get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
