from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import Link


@pytest.fixture
def make_user_links(db: Session) -> list[Link]:
    now = datetime.now(timezone.utc)
    links = []

    for i in range(3):
        link: Link = Link(
            short_id=f"active{i}",
            orig_url=f"https://example.com/{i}",
            user_id=1,
            created_at=now - timedelta(minutes=i), # Created 0, 1, 2 minutes ago
            expire_at=now + timedelta(minutes=10 - i),
            is_active=True
        )
        links.append(link)

    for i in range(2):
        link: Link = Link(
            short_id=f"expired{i}",
            orig_url=f"https://example.com/{i}",
            user_id=1,
            created_at=now - timedelta(hours=1 + i), # Created 1, 2 hours ago
            expire_at=now - timedelta(seconds=30 + i),
            is_active=True
        )
        links.append(link)

    for i in range(2):
        link: Link = Link(
            short_id=f"inactive{i}",
            orig_url=f"https://example.com/{i}",
            user_id=1,
            created_at=now - timedelta(minutes=5 + i), # Created 5, 6 minutes ago
            expire_at=now + timedelta(minutes=20),
            is_active=False
        )
        links.append(link)

    other = Link(
        short_id="otheruser",
        orig_url="https://other.com",
        user_id=2,
        created_at=now, # Created now
        expire_at=now + timedelta(minutes=5),
        is_active=True
    )
    links.append(other)

    for link in links:
        db.add(link)
    db.commit()
    return links
