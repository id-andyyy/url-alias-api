from sqlalchemy.exc import IntegrityError
from fastapi.testclient import TestClient

from app.main import app


@app.get("/api/test_integrity_error")
def integrity_error_route() -> None:
    raise IntegrityError("INSERT INTO ...", {}, Exception("unique constraint failed"))


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_integrity_error_handler(client: TestClient):
    response = client.get("/api/test_integrity_error")
    assert response.status_code == 400

    data = response.json()
    assert "message" in data
    assert "Database integrity error" in data["message"]
    assert "unique constraint failed" in data["message"]
