from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Text
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
    scrim_id: Mapped[int] = mapped_column(ForeignKey("scrim.id"))
    scrim: Mapped[int] = relationship(
        "Scrim",
    )
    secret: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    members: Mapped[list[TeamMember]] = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )


class TeamMember(Base):
    __tablename__ = "team_member"
    id: Mapped[int | None] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False, index=True
    )
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    scrim_id: Mapped[int] = mapped_column(
        ForeignKey("scrim.id", ondelete="CASCADE"), nullable=False
    )
    team: Mapped[Team] = relationship("Team", back_populates="members")
