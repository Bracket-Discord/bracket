from datetime import datetime, timedelta, timezone
import json
from typing import Any, cast
from fastapi import APIRouter, Depends, FastAPI, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from backend.db_funcs import get_active_session_by_id
from backend.middlewares.auth import is_authenticated
from backend.serializers import serialize_guild
from backend.utils import generate_random_string
from configs import settings
from core.bracket import bot
from backend.oauth import oauth2
from db.models.auth import DBSession, DBUser
from redis_manager import redis
from db import db_session

app = FastAPI()
router = APIRouter()


async def get_guilds_from_cache(user_id: str):
    cached = await redis.get(f"oauth:user:{user_id}:guilds")
    if cached:
        return json.loads(cached)
    return None


@router.get("/guilds")
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
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                )
                .returning(DBSession)
            )
            s = await session.scalar(stmt)
            return cast(DBSession, s)


def set_session_cookie(response: Response, value: str):
    response.set_cookie(
        key="session_id",
        value=value,
        httponly=False,  # TODO: change to True in production (requires HTTPS)
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
        secure=False,  # TODO: change to True in production (requires HTTPS)
    )


@router.get("/auth/callback")
async def oauth_callback(code: str, state: str, response: Response):
    token_data = await oauth2.fetch_token(code)
    access_token = token_data["access_token"]
    user_data = await oauth2.fetch_user(access_token)
    user = await find_or_create_user(user_data)
    session = await create_session(user.id, token_data)
    state_parsed = json.loads(state)
    set_session_cookie(response, session.id)

    return {
        "state": state_parsed,
        "session": session.id,
    }


@router.get("/auth/me")
async def oauth_me(user: DBUser = Depends(is_authenticated)):
    user_data = {
        "id": user.id,
        "discord_id": user.discord_id,
        "username": user.username,
        "discriminator": user.discriminator,
        "avatar": user.avatar,
        "email": user.email,
    }
    return {"user": user_data}


@router.get("/auth/login")
async def oauth_login(state: str | None = None):
    if not state:
        state = json.dumps({})
    else:
        try:
            json.loads(state)
        except Exception:
            state = json.dumps({})

    auth_url = oauth2.get_authorization_url(state)
    return RedirectResponse(auth_url)


if settings.environment == "development":
    ##############
    # For testing purposes only
    ##############
    ##############
    # WARNING: This endpoint should not be used in production
    ##############
    @router.get("/auth/login-with-session")
    async def login_with_session(session: str, response: Response):
        s = await get_active_session_by_id(session)
        if not s or not s.user:
            return {"error": "Invalid session"}
        set_session_cookie(response, session)
        return {"message": "Logged in with session"}


class CreateTournamentRequest(BaseModel):
    name: str
    game: str
    registration_start: datetime
    registration_end: datetime
    scrim_start: datetime
    scrim_end: datetime
    max_teams: int
    team_capacity: int
    subs_per_team: int
    description: str
    rules: str


class CreateTournamentResponse(BaseModel):
    message: str
    user: str
    tournament: CreateTournamentRequest


@router.post("/tournaments")
async def create_tournament(
    body: CreateTournamentRequest, user: DBUser = Depends(is_authenticated)
):
    return CreateTournamentResponse(
        message="Tournament created successfully", user=user.username, tournament=body
    )


app.include_router(router, prefix="/api")
