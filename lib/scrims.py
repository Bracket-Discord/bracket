from datetime import datetime
from pydantic import BaseModel
from core.bracket import bot
from db import db_session
from db.models import DBScrim


ERROR_GUILD_NOT_FOUND = "ERROR_GUILD_NOT_FOUND"


class CreateScrim(BaseModel):
    game: str
    guild_id: int
    name: str
    max_teams: int
    max_team_size: int
    registration_start_time: datetime


async def create_scrim(scrim: CreateScrim):
    guild = bot.get_guild(scrim.guild_id)
    if not guild:
        return {"error": "Guild not found", "code": ERROR_GUILD_NOT_FOUND}
    organizer_role = await guild.create_role(name="Organizer")
    participant_role = await guild.create_role(name="Participant")
    category = await guild.create_category(name=scrim.name)
    logs_channel = await guild.create_text_channel(name="logs", category=category)
    admin_channel = await guild.create_text_channel(name="admin", category=category)
    registration_channel = await guild.create_text_channel(
        name="register", category=category
    )
    # TODO: Setup permissions
    # TODO: Create a timer to open registration
    async with db_session() as session:
        new_scrim = DBScrim(
            game=scrim.game,
            guild_id=scrim.guild_id,
            name=scrim.name,
            max_teams=scrim.max_teams,
            max_team_size=scrim.max_team_size,
            organizer_role_id=organizer_role.id,
            participant_role_id=participant_role.id,
            category_id=category.id,
            logs_channel_id=logs_channel.id,
            admin_channel_id=admin_channel.id,
            registration_channel_id=registration_channel.id,
            registratin_start_time=scrim.registration_start_time,
        )
        session.add(new_scrim)
        await session.commit()
        await session.refresh(new_scrim)

    return new_scrim
