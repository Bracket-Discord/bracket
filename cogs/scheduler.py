from __future__ import annotations
import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Any, cast

import discord
import asyncpg
from sqlalchemy import select
from core.cog import Cog

from db import db_session
from db.models.task import DBTask

if TYPE_CHECKING:
    from core.bracket import BracketBot


class Scheduler(Cog):
    def __init__(self, bot: BracketBot):
        super().__init__(bot)
        self._have_data = asyncio.Event()
        self._current_task: Optional[DBTask] = None
        self._task = asyncio.create_task(self.dispatch_tasks())

    async def create_task(
        self,
        event: str,
        expires_at: datetime,
        /,
        *args: Tuple[Any],
        id: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        task = DBTask(
            event=event,
            id=id,
            extra={"args": args, "kwargs": kwargs},
            expires_at=expires_at,
        )
        async with db_session() as session:
            session.add(task)
            await session.commit()
            await session.flush()

        if (
            self._current_task is None
            or task.expires_at < self._current_task.expires_at
        ):
            print("Setting current task to", task.id)
            self._current_task = task
            self._have_data.set()

        return task

    async def get_active_task(self, days: int = 7) -> Optional[DBTask]:
        async with db_session() as session:
            now = datetime.now(tz=UTC)
            expires_at = now + timedelta(days=days)
            task = await session.scalar(
                select(DBTask).where(DBTask.expires_at <= expires_at).limit(1)
            )
            return task

    async def wait_for_active_task(self, days: int = 7):
        task = await self.get_active_task(days)
        if task is not None:
            self._have_data.set()
            return task

        self._have_data.clear()
        self._current_task = None
        print("Would need to wait for a task")
        await self._have_data.wait()
        task = await self.get_active_task(days)
        return cast(DBTask, task)

    async def dispatch_tasks(self) -> None:
        try:
            while not self.bot.is_closed():
                task = self._current_task = await self.wait_for_active_task()
                now = datetime.now(tz=UTC)
                if task.expires_at >= now:
                    print(
                        f"Waiting for task {task.id} to expire at {task.expires_at} "
                        f"({(task.expires_at - now).total_seconds()} seconds)"
                    )
                    await asyncio.sleep((task.expires_at - now).total_seconds())

                await self.call_task(task)
        except asyncio.CancelledError:
            raise
        except (OSError, discord.ConnectionClosed, asyncpg.PostgresConnectionError):
            self._task.cancel()
            self._task = asyncio.create_task(self.dispatch_tasks())

    async def call_task(self, task: DBTask):
        async with db_session() as session:
            await session.delete(task)
            await session.commit()

        print(
            "Dispatching Task",
            task.event + "_task_completed",
            task.extra["args"],
            task.extra["kwargs"],
        )
        self.bot.dispatch(
            task.event + "_task_completed", *task.extra["args"], **task.extra["kwargs"]
        )


setup = Scheduler.setup
