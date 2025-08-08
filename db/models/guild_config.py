from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from db.models.base import Base


class DBGuildConfig(Base):
    __tablename__ = "guild_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    admin_role_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
