from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.orm import Session

from app.crud.stats import crud_log_click, crud_get_stats_for_user_links, crud_get_stats_for_single_link
from app.exceptions import ClickLogError
from app.models import Link, Click, User
from tests.fixtures.links import test_links


def test_crud_log_click_success(db: Session, test_links: list[Link]):
    link: Link = test_links[0]
    crud_log_click(db, link.id)

    clicks: list[Click] = db.query(Click).filter(Click.link_id == link.id).all()
    assert len(clicks) == 1
    delta: timedelta = datetime.now(timezone.utc) - clicks[0].clicked_at.replace(tzinfo=timezone.utc)
    assert delta.total_seconds() < 5


def test_crud_log_click_integrity_error(db: Session):
    with pytest.raises(ClickLogError) as exc_info:
        crud_log_click(db, 9999)

    assert "Error while logging click" in str(exc_info.value)
    assert db.query(Click).filter(Click.link_id == 9999).count() == 0


def insert_clicks(db: Session, link: Link, times: list[datetime]) -> None:
    for t in times:
        click: Click = Click(link_id=link.id, clicked_at=t)
        db.add(click)

    db.commit()


def test_crud_get_stats_for_user_links_sorting(db: Session, test_user: User, test_links: list[Link]):
    link1, link2 = test_links[0], test_links[1]
    now: datetime = datetime.now(timezone.utc)

    times_link1: list[datetime] = [
        now - timedelta(minutes=10),
        now - timedelta(minutes=30),
        now - timedelta(hours=2),
        now - timedelta(days=2),
        now - timedelta(days=3),
    ]
    insert_clicks(db, link1, times_link1)

    times_link2: list[datetime] = [
        now - timedelta(minutes=5),
        now - timedelta(hours=3),
        now - timedelta(hours=5),
        now - timedelta(hours=10),
        now - timedelta(hours=20),
        now - timedelta(days=1, minutes=1),
    ]
    insert_clicks(db, link2, times_link2)

    stats_hour: list[tuple[str, str, int, int, int]] = crud_get_stats_for_user_links(db=db, user_id=test_user.id,
                                                                                     top=10, sort_by="hour")
    assert stats_hour[0][1] == link1.short_id
    assert stats_hour[0][2] == 2
    assert stats_hour[1][1] == link2.short_id
    assert stats_hour[1][2] == 1

    stats_day: list[tuple[str, str, int, int, int]] = crud_get_stats_for_user_links(db=db, user_id=test_user.id, top=10,
                                                                                    sort_by="day")
    assert stats_day[0][1] == link2.short_id
    assert stats_day[0][3] == 5
    assert stats_day[1][1] == link1.short_id
    assert stats_day[1][3] == 3

    stats_all: list[tuple[str, str, int, int, int]] = crud_get_stats_for_user_links(db=db, user_id=test_user.id, top=10,
                                                                                    sort_by="all")
    assert stats_all[0][1] == link2.short_id
    assert stats_all[0][4] == 6
    assert stats_all[1][1] == link1.short_id
    assert stats_all[1][4] == 5

    assert len(stats_all) == 7


def test_crud_get_stats_for_user_links_limit(db: Session, test_user: User, test_links: list[Link]):
    link1, link2 = test_links[0], test_links[1]
    now: datetime = datetime.now(timezone.utc)

    insert_clicks(db, link1, [now - timedelta(minutes=1)])
    insert_clicks(db, link2, [now - timedelta(minutes=2), now - timedelta(minutes=3)])

    stats_top: list[tuple[str, str, int, int, int]] = crud_get_stats_for_user_links(db=db, user_id=test_user.id, top=1,
                                                                                    sort_by="all")
    assert len(stats_top) == 1
    assert stats_top[0][1] == link2.short_id


def test_crud_get_stats_for_user_links_empty(db: Session, test_user: User):
    stats_empty: list[tuple[str, str, int, int, int]] = crud_get_stats_for_user_links(db=db, user_id=test_user.id)
    assert stats_empty == []


def test_crud_get_stats_for_single_link(db: Session, test_user: User, test_links: list[Link]):
    link: Link = test_links[0]
    now: datetime = datetime.now(timezone.utc)

    times: list[datetime] = [
        now - timedelta(minutes=1),
        now - timedelta(minutes=30),
        now - timedelta(hours=2),
        now - timedelta(days=2),
    ]
    insert_clicks(db, link, times)

    stats: tuple[str, str, int, int, int] = crud_get_stats_for_single_link(db=db, link=link)
    orig_url, short_id, cnt_hour, cnt_day, cnt_all = stats

    assert orig_url == link.orig_url
    assert short_id == link.short_id
    assert cnt_hour == 2
    assert cnt_day == 3
    assert cnt_all == 4

    fake_link: Link = Link(user_id=test_user.id, orig_url="x", short_id="nonexistent")
    result_none = crud_get_stats_for_single_link(db, link=fake_link)
    assert result_none is None