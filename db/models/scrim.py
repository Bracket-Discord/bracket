from __future__ import annotations
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum

from db.models.base import Base


class BestOf(Enum):
    BO1 = 1
    BO3 = 3
    BO5 = 5


class Scrim(Base):
    __tablename__ = "scrim"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    admin_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    participant_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    organizer_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    time: Mapped[datetime | None] = mapped_column(nullable=True)
    max_participants: Mapped[int] = mapped_column(nullable=False, default=10)
    max_team_size: Mapped[int] = mapped_column(nullable=False, default=5)
    best_of: Mapped[BestOf] = mapped_column(
        BigInteger, nullable=False, default=BestOf.BO1
    )
    rules: Mapped[str | None] = mapped_column(nullable=True, default=None)
    description: Mapped[str | None] = mapped_column(nullable=True, default=None)
