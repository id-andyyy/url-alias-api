from datetime import datetime, timezone

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models import User, Link
from app.schemas.stats import StatsListResponse, StatsResponse
from tests.fixtures.links import test_links
from tests.fixtures.user import override_get_current_user


def test_read_top_links_stats_default_params(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    fake_stats_list: list[tuple[str, str, int, int, int]] = [
        ("https://site.example/1", "AAA111", 3, 7, 20),
        ("https://site.example/2", "BBB222", 0, 2, 5),
    ]

    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_stats_for_user_links",
        lambda db, user_id, top, sort_by: fake_stats_list
    )

    response = client.get("/api/stats")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    parsed: StatsListResponse = StatsListResponse(**data)
    print(parsed)

    assert isinstance(parsed.items, list)
    assert len(parsed.items) == len(fake_stats_list)

    for idx, item in enumerate(parsed.items):
        orig_url, short_id, last_hour, last_day, all_clicks = fake_stats_list[idx]
        assert item.orig_url == orig_url
        assert item.short_url == f"http://testserver/{short_id}"
        assert item.last_hour_clicks == last_hour
        assert item.last_day_clicks == last_day
        assert item.all_clicks == all_clicks


def test_read_top_links_stats_with_query_params(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    fake_stats_list: list[tuple[str, str, int, int, int]] = [
        ("https://foo.bar/3", "CCC333", 1, 1, 2),
    ]

    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_stats_for_user_links",
        lambda db, user_id, top, sort_by: fake_stats_list
    )

    response = client.get("/api/stats/?top=5&sort_by=day")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    parsed: StatsListResponse = StatsListResponse(**data)

    assert len(parsed.items) == 1
    assert parsed.items[0].orig_url == fake_stats_list[0][0]
    assert parsed.items[0].short_url == f"http://testserver/{fake_stats_list[0][1]}"
    assert parsed.items[0].all_clicks == 2


def test_read_link_stats_not_found(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_link_by_short_id",
        lambda db, short_id: None
    )

    response = client.get("/api/stats/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == "Link not found"


def test_read_link_stats_forbidden_if_not_owner(
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
        test_user: User
):
    now: datetime = datetime.now(timezone.utc)
    other_link: Link = Link(
        short_id="XYZ123",
        orig_url="https://site.example/xyz",
        user_id=test_user.id + 1,
        created_at=now,
        expire_at=now,
        is_active=True
    )

    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_link_by_short_id",
        lambda db, short_id: other_link
    )

    response = client.get("/api/stats/XYZ123")
    assert response.status_code == status.HTTP_403_FORBIDDEN

    data = response.json()
    assert "You do not have permission" in data["detail"]


def test_read_link_stats_stats_not_found(
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
        test_user: User
):
    now: datetime = datetime.now(timezone.utc)
    own_link = Link(
        short_id="OWN001",
        orig_url="https://site.example/own",
        user_id=test_user.id,
        created_at=now,
        expire_at=now,
        is_active=True
    )

    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_link_by_short_id",
        lambda db, short_id: own_link
    )
    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_stats_for_single_link",
        lambda db, link: None
    )

    response = client.get("/api/stats/OWN001")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()
    assert data["detail"] == "Stats not found"


def test_read_link_stats_success(
        client: TestClient,
        monkeypatch: pytest.MonkeyPatch,
        test_user: User
):
    fake_single_stats: tuple[str, str, int, int, int] = (
        "https://site.example/XYZ", "XYZ999", 1, 4, 10
    )

    now: datetime = datetime.now(timezone.utc)
    link: Link = Link(
        short_id=fake_single_stats[1],
        orig_url=fake_single_stats[0],
        user_id=test_user.id,
        created_at=now,
        expire_at=now,
        is_active=True
    )

    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_link_by_short_id",
        lambda db, _short_id: link
    )
    monkeypatch.setattr(
        "app.api.routes.stats.crud_get_stats_for_single_link",
        lambda db, _link: fake_single_stats
    )

    response = client.get(f"/api/stats/{link.short_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    parsed: StatsResponse = StatsResponse(**data)

    orig_url, short_id, last_hour, last_day, all_clicks = fake_single_stats
    assert parsed.orig_url == orig_url
    assert parsed.short_url == f"http://testserver/{short_id}"
    assert parsed.last_hour_clicks == last_hour
    assert parsed.last_day_clicks == last_day
    assert parsed.all_clicks == all_clicks
