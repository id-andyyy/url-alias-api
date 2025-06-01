from sqlalchemy.orm import Session

from app.models import Link


def get_link_by_short_id(db: Session, short_id: str) -> Link | None:
    return db.query(Link).filter(Link.short_id == short_id).first()
