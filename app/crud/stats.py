from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Click


def log_click(db: Session, link_id: int) -> None:
    db.add(Click(link_id=link_id, clicked_at=datetime.now()))
    db.commit()