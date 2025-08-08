from datetime import UTC, datetime
from typing import Any
import uuid
from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from db.models.base import Base


class DBTask(Base):
    __tablename__ = "task"
    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    event: Mapped[str] = mapped_column(nullable=False)
    extra: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
