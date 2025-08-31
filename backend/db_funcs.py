from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql.base import select
from sqlalchemy.orm import selectinload

from db import db_session
from db.models.auth import DBSession


async def get_active_session_by_id(session_id: str):
    async with db_session() as session:
        stmt = (
            select(DBSession)
            .where(DBSession.id == session_id)
            .where(DBSession.expires_at > datetime.now(timezone.utc))
            .options(selectinload(DBSession.user))
        )
        result = await session.execute(stmt)
        s = result.scalar_one_or_none()
        return s
