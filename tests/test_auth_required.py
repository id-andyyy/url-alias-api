import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.user import crud_create_user
from app.models import User

PRIVATE_ENDPOINTS: list[tuple[str, str, dict[str, str]]] = [
    ("/api/links/", "get", {}),
    ("/api/links/", "post", {}),
    ("/api/links/{short_id}/deactivate", "patch", {"short_id": "test_short_id"}),
    ("/api/stats/", "get", {}),
    ("/api/stats/{short_id}", "get", {"short_id": "test_short_id"}),
]


@pytest.mark.parametrize("template, method, placeholders", PRIVATE_ENDPOINTS)
def test_auth_required(client: TestClient, template: str, method: str, placeholders: dict[str, str]) -> None:
    path = template.format(**placeholders)
    http_fn = getattr(client, method.lower())
    response = http_fn(path)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"].startswith("Basic")


@pytest.mark.parametrize("template, method, placeholders", PRIVATE_ENDPOINTS)
def test_invalid_credentials(client: TestClient, template: str, method: str, placeholders) -> None:
    path = template.format(**placeholders)
    http_fn = getattr(client, method.lower())
    response = http_fn(path, auth=("invalid_user", "invalid_password"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers["WWW-Authenticate"].startswith("Basic")


@pytest.mark.parametrize("template, method, placeholders", PRIVATE_ENDPOINTS)
def test_user_inactive(client: TestClient, db: Session, template: str, method: str, placeholders) -> None:
    username, password = "inactive_user", "inactive_user"
    try:
        user = crud_create_user(db, username=username, plain_password=password)
    except Exception:
        user = db.query(User).filter(User.username == username).first()
    user.is_active = False
    db.commit()

    path = template.format(**placeholders)
    http_fn = getattr(client, method.lower())
    response = http_fn(path, auth=(username, password))
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.headers["WWW-Authenticate"].startswith("Basic")
