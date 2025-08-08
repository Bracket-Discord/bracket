from sqlalchemy.sql import select
from db import db_session
from db.models.guild_config import DBGuildConfig
from db.models.tournament import DBTournament


async def fetch_guild_config(guild_id: int):
    async with db_session() as session:
        stmt = select(DBGuildConfig).where(DBGuildConfig.guild_id == guild_id)
        return await session.scalar(stmt)


async def fetch_tournament_by_id(tournament_id: int):
    async with db_session() as session:
        stmt = select(DBTournament).where(DBTournament.id == tournament_id)
        return await session.scalar(stmt)
