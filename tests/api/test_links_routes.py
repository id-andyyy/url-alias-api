from datetime import datetime, timezone, timedelta, tzinfo

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.exceptions import ShortIdGenerationError, LinkCreateError, LinkUpdateError
from app.models import Link, User
from tests.fixtures.links import test_links
from tests.fixtures.user import override_get_current_user


def test_create_link_success(client: TestClient, db: Session, test_user: User):
    expire_seconds: int = 3600
    payload: dict[str, any] = {
        "orig_url": "https://example.com/xyz?page=12&filter=price",
        "expire_seconds": expire_seconds
    }
    before: datetime = datetime.now(timezone.utc)
    response = client.post("/api/links", json=payload)
    after: datetime = datetime.now(timezone.utc)
    assert response.status_code == status.HTTP_201_CREATED

    data: dict[str, any] = response.json()
    assert "short_id" in data
    assert data["orig_url"] == "https://example.com/xyz?page=12&filter=price"
    assert data["user_id"] == test_user.id
    assert data["is_active"] is True
    assert data["short_url"] == f"http://testserver/{data['short_id']}"
    created_at: datetime = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")).replace(
        tzinfo=timezone.utc)
    assert before <= created_at <= after
    expire_at: datetime = datetime.fromisoformat(data["expire_at"].replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
    expected_earliest: datetime = created_at + timedelta(seconds=expire_seconds - 1)
    expected_latest: datetime = created_at + timedelta(seconds=expire_seconds + 1)
    assert expected_earliest <= expire_at <= expected_latest

    created: Link = db.query(Link).filter(Link.short_id == data["short_id"]).first()
    assert created is not None
    assert created.short_id == data["short_id"]
    assert created.orig_url == "https://example.com/xyz?page=12&filter=price"
    assert created.user_id == test_user.id


def test_create_link_shortid_error(monkeypatch: pytest.MonkeyPatch, client: TestClient, test_user: User):
    monkeypatch.setattr(
        "app.api.routes.links.generate_short_id",
        lambda db: (_ for _ in ()).throw(ShortIdGenerationError("cannot generate"))
    )

    payload: dict[str, any] = {
        "orig_url": "https://example.com/bad",
        "expire_seconds": 3600
    }
    response = client.post("/api/links", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot generate" in response.json()["detail"]


def test_create_link_crud_create_error(monkeypatch: pytest.MonkeyPatch, client: TestClient, test_user: User):
    def fake_generate(db: Session):
        return "fixedshortid"

    def fake_crud_create(
            db: Session,
            short_id: str,
            orig_url: str,
            user_id: int,
            expire_seconds: int,
            is_active: bool):
        raise LinkCreateError("crud failed")

    monkeypatch.setattr("app.api.routes.links.generate_short_id", fake_generate)
    monkeypatch.setattr("app.api.routes.links.crud_create_link", fake_crud_create)

    payload: dict[str, any] = {
        "orig_url": "https://example.com/error",
        "expire_seconds": 60
    }
    response = client.post("/api/links", json=payload)
    data: dict[str, any] = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "crud failed" in data["detail"]


def test_deactivate_link_success(db: Session, client: TestClient, test_user: User, test_links: list[Link]):
    active_link = next(
        filter(lambda link: link.is_active and link.expire_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc),
               test_links))
    short_id: int = active_link.short_id

    response = client.patch(f"/api/links/{short_id}/deactivate")
    assert response.status_code == status.HTTP_200_OK
    data: dict[str, any] = response.json()
    assert data["short_id"] == short_id
    assert data["is_active"] is False
    assert data["user_id"] == test_user.id

    updated: Link = db.query(Link).filter(Link.short_id == short_id).first()
    assert updated.is_active is False


def test_deactivate_link_not_found(client: TestClient):
    response = client.patch("/api/links/nonexisting/deactivate")
    data: dict[str, any] = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Link not found" in data["detail"]


def test_deactivate_link_permission_denied(
        db: Session,
        client: TestClient,
        test_user: User,
        test_links: list[Link]
):
    other_user: User = User(username="other_user", password_hash="passqord")
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    now: datetime = datetime.now(timezone.utc)
    foreign_link: Link = Link(
        short_id="foreign123",
        orig_url="https://evil.com",
        user_id=other_user.id,
        created_at=now,
        expire_at=now + timedelta(hours=1),
        is_active=True,
    )
    db.add(foreign_link)
    db.commit()

    response = client.patch(f"/api/links/{foreign_link.short_id}/deactivate")
    data: dict[str, any] = response.json()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "permission" in data["detail"]


def test_deactivate_link_crud_update_error(
        monkeypatch: pytest.MonkeyPatch,
        db: Session,
        client: TestClient,
        test_links: list[Link]
):
    link: Link = test_links[0]
    monkeypatch.setattr(
        "app.api.routes.links.crud_get_link_by_short_id",
        lambda db_s, s_id: link if s_id == link.short_id else None
    )

    def fake_deactivate(_db: Session, _link: Link):
        raise LinkUpdateError("cannot update")

    monkeypatch.setattr("app.api.routes.links.crud_deactivate_link", fake_deactivate)

    response = client.patch(f"/api/links/{link.short_id}/deactivate")
    data: dict[str, any] = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot update" in data["detail"]


def test_read_links_default_pagination(client: TestClient, test_links: list[Link]):
    response = client.get("/api/links")
    assert response.status_code == status.HTTP_200_OK

    data: dict[str, any] = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_items"] == len(test_links)
    assert data["total_pages"] == 1
    assert isinstance(data["items"], list)
    assert len(data["items"]) == len(test_links)

    for item in data["items"]:
        assert item["short_url"].startswith("http://testserver/")


def test_read_links_with_page_size_and_page(client: TestClient, test_links: list[Link]):
    response = client.get("/api/links/?page=2&page_size=3")
    assert response.status_code == status.HTTP_200_OK
    data: dict[str, any] = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 3
    assert data["total_items"] == len(test_links)
    assert data["total_pages"] == 3
    assert len(data["items"]) == 3


def test_read_links_filter_is_active_true(client: TestClient, test_links: list[Link]):
    response = client.get("/api/links/?is_active=true")
    assert response.status_code == status.HTTP_200_OK
    data: dict[str, any] = response.json()
    assert data["total_items"] == 5
    assert len(data["items"]) == 5


def test_read_links_filter_is_active_false(client: TestClient, test_links: list[Link]):
    response = client.get("/api/links/?is_active=false")
    assert response.status_code == status.HTTP_200_OK

    data: dict[str, any] = response.json()
    assert data["total_items"] == 2
    assert len(data["items"]) == 2

    for item in data["items"]:
        assert item["is_active"] is False


def test_read_links_filter_is_valid_true(client: TestClient, test_links: list[Link]):
    now: datetime = datetime.now(timezone.utc)
    valid_links: list[Link] = [link for link in test_links if link.expire_at.replace(tzinfo=timezone.utc) > now]
    assert len(valid_links) == 5

    response = client.get("/api/links/?is_valid=true")
    assert response.status_code == status.HTTP_200_OK

    data: dict[str, any] = response.json()
    assert data["total_items"] == len(valid_links)
    assert len(data["items"]) == len(valid_links)

    for item in data["items"]:
        expire_at: datetime = datetime.fromisoformat(item["expire_at"].replace("Z", "+00:00")).replace(
            tzinfo=timezone.utc)
        assert expire_at > now


def test_read_links_filter_is_valid_false(client: TestClient, test_links: list[Link]):
    now = datetime.now(timezone.utc)
    invalid_links = [link for link in test_links if link.expire_at.replace(tzinfo=timezone.utc) < now]
    assert len(invalid_links) == 2

    response = client.get("/api/links/?is_valid=false")
    assert response.status_code == status.HTTP_200_OK
    data: dict[str, any] = response.json()
    assert data["total_items"] == len(invalid_links)
    assert len(data["items"]) == len(invalid_links)
    for item in data["items"]:
        expire_at: datetime = datetime.fromisoformat(item["expire_at"].replace("Z", "+00:00")).replace(
            tzinfo=timezone.utc)
        assert expire_at < now
