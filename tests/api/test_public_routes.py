import pytest
from fastapi import status
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.exceptions import ClickLogError
from app.models import Link
import app.api.routes.public as public_module
from tests.fixtures.links import test_links


@pytest.mark.parametrize(
    "short_id, expected_url",
    [
        ("active0", "https://example.com/0"),
        ("active1", "https://example.com/1"),
        ("active2", "https://example.com/2"),
    ]
)
def test_redirect_active_link(client: TestClient, test_links: list[Link], short_id: str, expected_url: str):
    response = client.get(f"/{short_id}", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == expected_url


def test_redirect_nonexistent_link(client: TestClient):
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Link not found"


@pytest.mark.parametrize(
    "short_id",
    [
        "inactive0",
        "inactive1",
    ],
)
def test_redirect_inactive_link(client: TestClient, test_links: list[Link], short_id: str):
    response = client.get(f"/{short_id}", follow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Link is inactive"


@pytest.mark.parametrize(
    "short_id",
    [
        "expired0",
        "expired1",
    ],
)
def test_redirect_expired_link(client: TestClient, test_links: list[Link], short_id: str):
    response = client.get(f"/{short_id}", follow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Link has expired"


def test_click_logging_success(monkeypatch: pytest.MonkeyPatch, client: TestClient, test_links: list[Link]):
    calls = {"count": 0}

    def fake_log_click(db: Session, link_id: int):
        calls["count"] += 1

    monkeypatch.setattr(public_module, "crud_log_click", fake_log_click)

    response = client.get("/active0", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert calls["count"] == 1


def test_click_logging_failure(monkeypatch, client: TestClient, caplog, test_links: list[Link]):
    def fake_log_click_error(db: Session, link_id: int):
        raise ClickLogError("fail to log click")

    monkeypatch.setattr(public_module, "crud_log_click", fake_log_click_error)

    caplog.set_level("ERROR", logger=public_module.logger.name)

    response = client.get("/active1", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    matching = [rec for rec in caplog.records if "Error logging click for link" in rec.getMessage()]
    assert len(matching) == 1
    assert "fail to log click" in matching[0].getMessage()
