from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class DBTournament(Base):
    __tablename__ = "tournament"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
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
