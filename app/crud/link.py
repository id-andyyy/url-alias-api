from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import LinkCreateError, LinkUpdateError
from app.models import Link


def crud_get_link_by_short_id(db: Session, short_id: str) -> Link | None:
    return db.query(Link).filter(Link.short_id == short_id).first()


def crud_get_user_links(
        db: Session,
        user_id: int,
        is_active: bool | None = True,
        limit: int = 10,
        offset: int = 0
) -> tuple[list[Link], int]:
    query = db.query(Link).filter(Link.user_id == user_id)

    if is_active is not None:
        query = query.filter(Link.is_active == is_active)

    total: int = query.count()

    return query.offset(offset).limit(limit).all(), total


def crud_get_active_user_link_by_orig_url(db: Session, orig_url: str, user_id: int) -> Link | None:
    return db.query(Link).filter(
        Link.orig_url == orig_url,
        Link.user_id == user_id,
        Link.is_active == True,
        Link.expire_at > datetime.now(timezone.utc)
    ).first()


def crud_create_link(
        db: Session,
        short_id: str,
        orig_url: str,
        user_id: int,
        expire_seconds: int,
        is_active: bool
) -> Link:
    expire_at: datetime = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)

    new_link: Link = Link(
        short_id=short_id,
        orig_url=orig_url,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        expire_at=expire_at,
        is_active=is_active
    )
    db.add(new_link)
    try:
        db.commit()
        db.refresh(new_link)
    except IntegrityError:
        db.rollback()
        raise LinkCreateError("Error while creating a link")

    return new_link


def crud_deactivate_link(
        db: Session,
        link: Link
) -> Link | None:
    link.is_active = False
    db.add(link)

    try:
        db.commit()
        db.refresh(link)
    except IntegrityError:
        db.rollback()
        raise LinkUpdateError("Error while deactivating a link")

    return link
