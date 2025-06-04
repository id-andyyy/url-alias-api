from datetime import datetime, timezone, timedelta, tzinfo

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.link import crud_get_link_by_short_id, crud_create_link, crud_get_user_links, crud_deactivate_link
from app.exceptions import LinkCreateError, LinkUpdateError
from app.models import Link, User
from tests.fixtures.links import test_links


def test_get_link_by_short_id_returns_none_if_not_exists(db: Session):
    link: Link | None = crud_get_link_by_short_id(db, short_id="nonexistentlink")
    assert link is None


def test_get_link_by_short_id_returns_link_if_exists(db: Session, test_user: User):
    link: Link = Link(
        short_id="existinglink",
        orig_url="https://example.com",
        user_id=test_user.id,
        created_at=datetime.now(timezone.utc),
        expire_at=datetime.now(timezone.utc) + timedelta(days=1),
        is_active=True
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    fetched: Link | None = crud_get_link_by_short_id(db, short_id="existinglink")
    assert isinstance(fetched, Link)
    assert fetched.id == link.id
    assert fetched.short_id == link.short_id
    assert fetched.orig_url == link.orig_url
    assert fetched.user_id == link.user_id
    assert fetched.created_at == link.created_at
    assert fetched.expire_at == link.expire_at
    assert fetched.is_active == link.is_active


def test_create_link_success(db: Session, test_user: User):
    short_id: str = "newlink"
    orig_url: str = "https://newexample.com"
    user_id: int = test_user.id
    expire_seconds: int = 3600
    is_active: bool = True

    before: datetime = datetime.now(timezone.utc)
    link: Link = crud_create_link(db, short_id, orig_url, user_id, expire_seconds, is_active)
    after: datetime = datetime.now(timezone.utc)

    assert isinstance(link, Link)
    assert link.short_id == short_id
    assert link.orig_url == orig_url
    assert link.user_id == user_id
    created_at: datetime = link.created_at.replace(tzinfo=timezone.utc)
    expire_at: datetime = link.expire_at.replace(tzinfo=timezone.utc)
    assert before <= created_at <= after
    expected_earliest: datetime = created_at + timedelta(seconds=expire_seconds - 1)
    expected_latest: datetime = created_at + timedelta(seconds=expire_seconds + 1)
    assert expected_earliest <= expire_at <= expected_latest
    assert link.is_active == link.is_active

    fetched: Link = crud_get_link_by_short_id(db, short_id)
    assert fetched.id == link.id


def test_create_link_raises_link_create_error_on_integrity_error(monkeypatch: pytest.MonkeyPatch, db: Session, test_user: User):
    def fake_commit():
        raise IntegrityError(statement=None, params=None, orig=None)

    monkeypatch.setattr(db, "commit", fake_commit)

    with pytest.raises(LinkCreateError) as exc_info:
        crud_create_link(
            db=db,
            short_id="newlink",
            orig_url="https://newexample.com",
            user_id=test_user.id,
            expire_seconds=3600,
            is_active=True
        )

    assert "Error while creating a link" in str(exc_info.value)


def test_get_user_links_default_filters(db: Session, test_user: User, test_links: list[Link]):
    results, total = crud_get_user_links(db=db, user_id=test_user.id, is_valid=True, is_active=True)

    assert total == 3
    assert len(results) == 3
    for link in results:
        assert link.user_id == test_user.id
        assert link.is_active is True
        assert link.expire_at.replace(tzinfo=timezone.utc) >= datetime.now(timezone.utc)


def test_get_user_links_expired(db: Session, test_user: User, test_links: list[Link]):
    results, total = crud_get_user_links(db=db, user_id=test_user.id, is_valid=False, is_active=True)

    assert total == 2
    assert len(results) == 2
    for link in results:
        assert link.user_id == test_user.id
        assert link.is_active is True
        assert link.expire_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)


def test_get_user_links_inactive(db: Session, test_user: User, test_links: list[Link]):
    results, total = crud_get_user_links(db=db, user_id=test_user.id, is_valid=True, is_active=False)

    assert total == 2
    assert len(results) == 2
    for link in results:
        assert link.user_id == test_user.id
        assert link.is_active is False
        assert link.expire_at.replace(tzinfo=timezone.utc) >= datetime.now(timezone.utc)


def test_get_user_links_pagination(db: Session, test_user: User, test_links: list[Link]):
    results, total = crud_get_user_links(db=db, user_id=test_user.id, is_valid=True, is_active=True, limit=2, offset=1)

    assert total == 3
    assert len(results) == 2
    for link in results:
        assert link.user_id == test_user.id
        assert link.is_active is True
        assert link.expire_at.replace(tzinfo=timezone.utc) >= datetime.now(timezone.utc)


def test_create_link_and_deactivate_and_update(db: Session, test_user: User):
    link: Link = crud_create_link(
        db=db,
        short_id="to_deactivate",
        orig_url="https://deact.com",
        user_id=test_user.id,
        expire_seconds=60,
        is_active=True
    )
    assert link.is_active is True

    deactivated_link: Link = crud_deactivate_link(db, link)
    assert deactivated_link.is_active is False

    fetched = crud_get_link_by_short_id(db, short_id="to_deactivate")
    assert fetched.is_active is False


def test_deactivate_link_raises_on_integrity_error(monkeypatch: pytest.MonkeyPatch, db: Session, test_user: User):
    now = datetime.now(timezone.utc)
    link = Link(
        short_id="willfail",
        orig_url="https://fail.com",
        user_id=test_user.id,
        created_at=now,
        expire_at=now + timedelta(minutes=5),
        is_active=True
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    def fake_commit():
        raise IntegrityError(statement=None, params=None, orig=None)

    monkeypatch.setattr(db, "commit", fake_commit)

    with pytest.raises(LinkUpdateError) as exc_info:
        crud_deactivate_link(db, link)

    assert "Error while deactivating a link" in str(exc_info.value)
