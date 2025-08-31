import discord
from typing import Dict, Any

from db.models.scrim import DBScrim


def serialize_role(role: discord.Role) -> Dict[str, Any]:
    return {
        "id": role.id,
        "name": role.name,
        "color": role.color.value,
        "position": role.position,
        "permissions": role.permissions.value,
        "hoist": role.hoist,
        "managed": role.managed,
        "mentionable": role.mentionable,
    }


def serialize_channel(channel: discord.abc.GuildChannel) -> Dict[str, Any]:
    return {
        "id": channel.id,
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "nsfw": getattr(channel, "nsfw", False),
        "topic": getattr(channel, "topic", None),
        "bitrate": getattr(channel, "bitrate", None),
        "user_limit": getattr(channel, "user_limit", None),
    }


def serialize_guild(guild: discord.Guild) -> Dict[str, Any]:
    return {
        "id": guild.id,
        "name": guild.name,
        "member_count": guild.member_count,
        "owner_id": guild.owner_id,
        "icon_url": str(guild.icon.url) if guild.icon else None,
        "roles": [serialize_role(role) for role in guild.roles],
        "channels": [serialize_channel(channel) for channel in guild.channels],
    }


def serialize_db_scrim(scrim: DBScrim) -> Dict[str, Any]:
    return {
        "id": scrim.id,
        "name": scrim.name,
        "game": scrim.game,
        "guild_id": scrim.guild_id,
        "max_teams": scrim.max_teams,
        "max_team_size": scrim.max_team_size,
        "registratin_start_time": scrim.registratin_start_time.isoformat()
        if scrim.registratin_start_time
        else None,
        "category_id": scrim.category_id,
        "admin_channel_id": scrim.admin_channel_id,
        "registration_channel_id": scrim.registration_channel_id,
        "logs_channel_id": scrim.logs_channel_id,
        "created_at": scrim.created_at.isoformat(),
    }
