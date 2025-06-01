from datetime import datetime
from sqlite3 import IntegrityError

from sqlalchemy.orm import Session

from app.exceptions import ClickLogError
from app.models import Click


def crud_log_click(db: Session, link_id: int) -> None:
    click: Click = Click(link_id=link_id, clicked_at=datetime.now())
    db.add(click)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ClickLogError("Error while logging click")