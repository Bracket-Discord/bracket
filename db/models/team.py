from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class Team(Base):
    __tablename__ = "team"
    id: Mapped[int | None] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    captain_id: Mapped[int] = mapped_column(BigInteger, index=True)
    max_size: Mapped[int] = mapped_column(nullable=False, default=5)
    current_size: Mapped[int] = mapped_column(nullable=False, default=0)
    scrim_id: Mapped[int] = mapped_column(ForeignKey("scrim.id"))
    scrim: Mapped[int] = relationship(
        "Scrim",
    )
