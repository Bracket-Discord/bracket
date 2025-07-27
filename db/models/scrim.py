from datetime import datetime
from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Scrim(Base):
    __tablename__ = "scrim"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    admin_channel_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    participant_role_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    organizer_role_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    scrim_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
