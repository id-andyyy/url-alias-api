from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import Link, User


@pytest.fixture
def test_links(db: Session, test_user: User) -> list[Link]:
    now: datetime = datetime.now(timezone.utc)
    links: list[Link] = []

    for i in range(3):
        link: Link = Link(
            short_id=f"active{i}",
            orig_url=f"https://example.com/{i}",
            user_id=test_user.id,
            created_at=now - timedelta(minutes=i),
            expire_at=now + timedelta(minutes=10 - i),
            is_active=True
        )
        links.append(link)

    for i in range(2):
        link: Link = Link(
            short_id=f"expired{i}",
            orig_url=f"https://example.com/{i}",
            user_id=test_user.id,
            created_at=now - timedelta(hours=1 + i),
            expire_at=now - timedelta(seconds=30 + i),
            is_active=True
        )
        links.append(link)

    for i in range(2):
        link: Link = Link(
            short_id=f"inactive{i}",
            orig_url=f"https://example.com/{i}",
            user_id=test_user.id,
            created_at=now - timedelta(minutes=5 + i),
            expire_at=now + timedelta(minutes=20),
            is_active=False
        )
        links.append(link)

    for link in links:
        db.add(link)
    db.commit()
    return links
