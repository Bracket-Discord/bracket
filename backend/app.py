import json
from typing import Any, cast
from fastapi import Cookie, FastAPI, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql.base import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from backend.serializers import serialize_guild
from backend.utils import generate_random_string
from core.bracket import bot
from backend.oauth import oauth2
from db.models.auth import DBSession, DBUser
from redis_manager import redis
from db import db_session

app = FastAPI()


async def get_session_by_id(session_id: str):
    async with db_session() as session:
        stmt = (
            select(DBSession)
            .where(DBSession.id == session_id)
            .options(selectinload(DBSession.user))
        )
        result = await session.execute(stmt)
        s = result.scalar_one_or_none()
        return s


async def get_guilds_from_cache(user_id: str):
    cached = await redis.get(f"oauth:user:{user_id}:guilds")
    if cached:
        return json.loads(cached)
    return None


@app.get("/guilds")
async def get_guilds():
    return [serialize_guild(guild) for guild in bot.guilds]


async def find_or_create_user(discord_user: dict[str, Any]):
    async with db_session() as session:
        async with session.begin():
            stmt = (
                insert(DBUser)
                .values(
                    discord_id=int(discord_user["id"]),
                    username=discord_user["username"],
                    discriminator=discord_user["discriminator"],
                    avatar=discord_user.get("avatar"),
                )
                .on_conflict_do_update(
                    index_elements=[DBUser.discord_id],
                    set_={
                        "username": discord_user["username"],
                        "discriminator": discord_user["discriminator"],
                        "avatar": discord_user.get("avatar"),
                        "email": func.coalesce(discord_user.get("email"), DBUser.email),
                    },
                )
                .returning(DBUser)
            )
            result = await session.execute(stmt)
            db_user = result.scalar_one()

            return db_user


async def create_session(user_id: int, token_data: dict[str, Any]):
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    access_token_expires_at = token_data["expires_in"]
    async with db_session() as session:
        async with session.begin():
            stmt = (
                insert(DBSession)
                .values(
                    id=generate_random_string(32),
                    user_id=user_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    access_token_expires_at=access_token_expires_at,
                )
                .returning(DBSession)
            )
            s = await session.scalar(stmt)
            return cast(DBSession, s)


@app.get("/oauth/callback")
async def oauth_callback(code: str, state: str, response: Response):
    try:
        token_data = await oauth2.fetch_token(code)
        access_token = token_data["access_token"]
        user_data = await oauth2.fetch_user(access_token)
        user = await find_or_create_user(user_data)
        session = await create_session(user.id, token_data)
        state_parsed = json.loads(state)
        response.set_cookie(
            key="session",
            value=session.id,
            httponly=False,  # TODO: change to True in production (requires HTTPS)
            samesite="lax",
            max_age=30 * 24 * 60 * 60,  # 30 days
            secure=False,  # TODO: change to True in production (requires HTTPS)
        )

        return {
            "state": state_parsed,
            "session": session.id,
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/oauth/me")
async def oauth_me(session: str = Cookie()):
    s = await get_session_by_id(session)
    if not s:
        return {"error": "Invalid session"}

    user = s.user
    if not user:
        return {"error": "Invalid session"}
    user_data = {
        "id": user.id,
        "discord_id": user.discord_id,
        "username": user.username,
        "discriminator": user.discriminator,
        "avatar": user.avatar,
        "email": user.email,
    }
    return {"user": user_data}


@app.get("/oauth/login")
async def oauth_login(state: str):
    try:
        json.loads(state)
    except Exception:
        state = json.dumps({})

    auth_url = oauth2.get_authorization_url(state)
    return RedirectResponse(auth_url)
