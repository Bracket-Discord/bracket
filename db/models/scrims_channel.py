from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base

class ScrimsChannel(Base):
    __tablename__ = "scrims_channel"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
