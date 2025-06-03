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


def crud_get_stats_for_user_links(db: Session, user_id: int, top: int = 10, sort_by: str = "all") -> list[
    tuple[str, str, int, int, int]]:
    now: datetime = datetime.now(timezone.utc)
    one_hour_ago: datetime = now - timedelta(hours=1)
    one_day_ago: datetime = now - timedelta(days=1)

    last_hour_cnt = func.count(Click.id).filter(Click.clicked_at >= one_hour_ago).label("last_hour_clicks")
    last_day_cnt = func.count(Click.id).filter(Click.clicked_at >= one_day_ago).label("last_day_clicks")
    all_cnt = func.count(Click.id).label("all_clicks")

    query = (
        db.query(
            Link.orig_url,
            Link.short_id,
            last_hour_cnt,
            last_day_cnt,
            all_cnt
        )
        .filter(Link.user_id == user_id)
        .outerjoin(Click, Click.link_id == Link.id)
        .group_by(Link.id)
    )

    if sort_by == "hour":
        query = query.order_by(desc(last_hour_cnt))
    elif sort_by == "day":
        query = query.order_by(desc(last_day_cnt))
    else:
        query = query.order_by(desc(all_cnt))

    query = query.limit(top)

    result = query.all()
    stats: list[tuple[str, str, int, int, int]] = [
        (row.orig_url, row.short_id, row.last_hour_clicks, row.last_day_clicks, row.all_clicks) for row in result]
    return stats


def crud_get_stats_for_single_link(db: Session, link: Link) -> tuple[str, str, int, int, int] | None:
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
        .filter(Link.user_id == link.user_id, Link.short_id == link.short_id)
        .outerjoin(Click, Click.link_id == Link.id)
        .group_by(Link.id)
    )

    return query.first()
