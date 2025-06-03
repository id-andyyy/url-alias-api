from datetime import datetime, timezone, timedelta

from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ClickLogError
from app.models import Click, Link


def crud_log_click(db: Session, link_id: int) -> None:
    click: Click = Click(link_id=link_id, clicked_at=datetime.now(timezone.utc))
    db.add(click)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ClickLogError("Error while logging click")


def crud_get_link_stats(db: Session, user_id: int, top: int = 10, sort_by: str = "all") -> list[
    tuple[str, str, int, int, int]]:
    print(">>> crud_get_link_stats вызван (А ТЕПЕРЬ ПОЙДЕМ ВЫПОЛНЯТЬ query.all())")

    now: datetime = datetime.now(timezone.utc)
    one_hour_ago: datetime = now - timedelta(hours=1)
    one_day_ago: datetime = now - timedelta(days=1)

    query = (
        db.query(
            Link.orig_url,
            Link.short_id,
            func.count(Click.id).filter(Click.clicked_at >= one_hour_ago).label("last_hour_clicks"),
            func.count(Click.id).filter(Click.clicked_at >= one_day_ago).label("last_day_clicks"),
            func.count(Click.id).label("all_clicks")
        )
        .outerjoin(Click, Click.link_id == Link.id)
        .filter(Link.user_id == user_id)
        .group_by(Link.id)
    )

    if sort_by == "hour":
        query = query.order_by(desc("last_hour_clicks"))
    elif sort_by == "day":
        query = query.order_by(desc("last_day_clicks"))
    else:
        query = query.order_by(desc("all_clicks"))

    query = query.limit(top)

    result = query.all()
    stats: list[tuple[str, str, int, int, int]] = [
        (row.orig_url, row.short_id, row.last_hour_clicks, row.last_day_clicks, row.all_clicks) for row in result]
    print(f">>> Получено {len(result)} строк из links")
    return stats
