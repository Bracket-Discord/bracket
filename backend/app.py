from typing import Any, Dict
import discord
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from core.bracket import bot
from backend.oauth import oauth2

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


@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    try:
        token_data = await oauth2.fetch_token(code)
        access_token = token_data["access_token"]
        user_data = await oauth2.fetch_user(access_token)
        guilds_data = await oauth2.fetch_guilds(access_token)
        return {
            "user": user_data,
            "guilds": guilds_data,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/oauth/login")
async def oauth_login():
    state = "random_state_string"
    auth_url = oauth2.get_authorization_url(state)
    return RedirectResponse(auth_url)
