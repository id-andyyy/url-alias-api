from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing_extensions import Annotated

from app.db.base import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[intpk]
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id", ondelete="CASCADE"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    link: Mapped["Link"] = relationship(
        back_populates="clicks"
    )
