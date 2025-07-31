from sqlalchemy.sql.functions import count

from sqlalchemy import select
from db import get_db
from db.models.scrim import Scrim
from db.models.team import Team, TeamMember


async def get_scrim_member(scrim_id: int, user_id: int):
    """
    Fetch a scrim member by scrim ID and user ID.
    Args:
        scrim_id (int): The ID of the scrim.
        user_id (int): The ID of the user.
    Returns:
        TeamMember: The team member associated with the scrim and user, or None if not found.
    """
    async with get_db() as session:
        stmt = select(TeamMember).where(
            TeamMember.scrim_id == scrim_id,
            TeamMember.user_id == user_id,
        )
        return (await session.execute(stmt)).scalar_one_or_none()


async def get_team_by_id(team_id: int):
    """Fetch a team by its ID."""
    async with get_db() as session:
        stmt = select(Team).where(Team.id == team_id)
        return (await session.execute(stmt)).scalar_one_or_none()


async def get_scrim_by_id(scrim_id: int):
    """Fetch a scrim by its ID."""
    async with get_db() as session:
        stmt = select(Scrim).where(Scrim.id == scrim_id)
        return (await session.execute(stmt)).scalar_one_or_none()


async def get_scrim_by_register_channel_id(channel_id: int):
    async with get_db() as session:
        stmt = select(Scrim).where(Scrim.register_channel_id == channel_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def get_team_member_count(team_id: int) -> int:
    async with get_db() as session:
        stmt = select(count(TeamMember.id)).where(
            TeamMember.team_id == team_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() or 0


async def get_team_by_secret(secret: str):
    async with get_db() as session:
        stmt = select(Team).where(Team.secret == secret)
        return (await session.execute(stmt)).scalar_one_or_none()
