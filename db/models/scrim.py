from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class DBScrim(Base):
    __tablename__ = "scrim"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    game: Mapped[str] = mapped_column(nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    max_teams: Mapped[int] = mapped_column(nullable=False)
    max_team_size: Mapped[int] = mapped_column(nullable=False)
    organizer_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    participant_role_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    registratin_start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    category_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    admin_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    registration_channel_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    logs_channel_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(tz=UTC),
    )
