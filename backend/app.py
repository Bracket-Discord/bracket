from typing import Any, Dict
import discord
from fastapi import FastAPI
from core.bracket import bot

app = FastAPI()


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


@app.get("/guilds")
async def get_guilds():
    return [serialize_guild(guild) for guild in bot.guilds]
