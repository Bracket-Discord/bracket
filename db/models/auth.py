from datetime import datetime, timezone
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import MappedColumn, mapped_column, relationship
from db.models.base import Base
from sqlalchemy.types import DateTime


class DBUser(Base):
    __tablename__ = "user"
    id: MappedColumn[int] = mapped_column(primary_key=True)
    discord_id: MappedColumn[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    username: MappedColumn[str] = mapped_column(nullable=False)
    discriminator: MappedColumn[str] = mapped_column(nullable=False)
    avatar: MappedColumn[str] = mapped_column(nullable=True)
    sessions = relationship("DBSession", back_populates="user")
    email: MappedColumn[str] = mapped_column(nullable=True)


class DBSession(Base):
    __tablename__ = "session"
    id: MappedColumn[str] = mapped_column(primary_key=True)
    user_id: MappedColumn[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    access_token: MappedColumn[str] = mapped_column(nullable=False)
    access_token_expires_at: MappedColumn[int] = mapped_column(nullable=False)
    refresh_token: MappedColumn[str] = mapped_column(nullable=False)
    expires_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    ip_address: MappedColumn[str] = mapped_column(nullable=True)
    user_agent: MappedColumn[str] = mapped_column(nullable=True)
    user = relationship(DBUser)
