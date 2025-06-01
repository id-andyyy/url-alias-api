from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Link


def crud_get_link_by_short_id(db: Session, short_id: str) -> Link | None:
    return db.query(Link).filter(Link.short_id == short_id).first()


def crud_get_link_by_orig_url_and_user_id(db: Session, orig_url: str, user_id: int) -> Link | None:
    return db.query(Link).filter(
        Link.orig_url == orig_url,
        Link.user_id == user_id,
        Link.is_active == True,
        Link.expire_at > datetime.now()
    ).first()


def crud_create_link(
        db: Session,
        short_id: str,
        orig_url: str,
        user_id: int,
        expire_seconds: int,
        is_active: bool
) -> Link:
    expire_at: datetime = datetime.now() + timedelta(seconds=expire_seconds)

    new_link: Link = Link(
        short_id=short_id,
        orig_url=orig_url,
        user_id=user_id,
        created_at=datetime.now(),
        expire_at=expire_at,
        is_active=is_active
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return new_link
