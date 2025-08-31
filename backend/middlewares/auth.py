from fastapi import HTTPException, Request

from backend.db_funcs import get_active_session_by_id
from db.models.auth import DBUser


async def is_authenticated(request: Request):
    session_id = request.cookies.get("session_id")
    user: DBUser | None = None
    if session_id:
        session = await get_active_session_by_id(session_id)
        user = session.user if session else None
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user
