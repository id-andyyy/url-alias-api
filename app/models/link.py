from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing_extensions import Annotated

from app.db.base import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]


class Link(Base):
    __tablename__ = "links"

    id: Mapped[intpk]
    short_id: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    orig_url: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(timezone.utc))
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    owner: Mapped["User"] = relationship(
        back_populates="links"
    )
    clicks: Mapped[list["Click"]] = relationship(
        back_populates="link",
        cascade="all, delete-orphan"
    )
