from __future__ import annotations
from datetime import datetime

from sqlalchemy import BigInteger, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from data.scrim_config import BestOf, BracketType, TournamentType
from db.models.base import Base


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
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_opening_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    registration_closing_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    teamcap: Mapped[int] = mapped_column(nullable=False)
    max_team_size: Mapped[int] = mapped_column(nullable=False)
    best_of: Mapped[BestOf] = mapped_column(Integer, nullable=False)
    tournament_type: Mapped[TournamentType] = mapped_column(Integer, nullable=False)
    bracket_type: Mapped[BracketType] = mapped_column(Integer, nullable=False)

    prize: Mapped[str | None] = mapped_column(nullable=True)

    rules: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)

    logs_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    register_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    announcements_channel_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    registration_open: Mapped[bool] = mapped_column(nullable=False, default=False)
