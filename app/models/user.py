from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing_extensions import Annotated

from app.db.base import Base

intpk = Annotated[int, mapped_column(primary_key=True, index=True)]


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    links: Mapped[list["Link"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )