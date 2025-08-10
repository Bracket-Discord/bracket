from sqlalchemy.sql import select
from db import db_session
from db.models.guild_config import DBGuildConfig
from db.models.team import DBTeam
from db.models.tournament import DBTournament


async def fetch_guild_config(guild_id: int):
    async with db_session() as session:
        stmt = select(DBGuildConfig).where(DBGuildConfig.guild_id == guild_id)
        return await session.scalar(stmt)


async def fetch_tournament_by_id(tournament_id: int):
    async with db_session() as session:
        stmt = select(DBTournament).where(DBTournament.id == tournament_id)

        return await session.scalar(stmt)


async def create_team(name: str, captain_id: int):
    async with db_session() as session:
        new_team = DBTeam(name=name, captain_id=captain_id, secret="123")
        session.add(new_team)
        await session.commit()
        return new_team


async def fetch_team_by_id(team_id: int):
    async with db_session() as session:
        stmt = select(DBTeam).where(DBTeam.id == team_id)
        return await session.scalar(stmt)
