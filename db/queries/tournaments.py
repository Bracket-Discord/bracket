from sqlalchemy.sql import select
from db import db_session
from db.models.guild_config import DBGuildConfig


async def fetch_guild_config(guild_id: int):
    async with db_session() as session:
        stmt = select(DBGuildConfig).where(DBGuildConfig.guild_id == guild_id)
        result = await session.execute(stmt)
        guild_config = result.scalars().first()
        return guild_config
