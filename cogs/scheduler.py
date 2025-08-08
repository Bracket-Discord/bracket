from __future__ import annotations
import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Any, cast

import discord
import asyncpg
from sqlalchemy import select
from core.cog import Cog

from core.logger import setup_logger
from db import db_session
from db.models.task import DBTask

if TYPE_CHECKING:
    from core.bracket import BracketBot


class Scheduler(Cog):
    def __init__(self, bot: BracketBot):
        super().__init__(bot)
        self.log = setup_logger("scheduler")
        self._have_data = asyncio.Event()
        self._current_task: Optional[DBTask] = None
        self._task = asyncio.create_task(self.dispatch_tasks())
        self.log.info("Scheduler initialized and dispatch task started.")

    async def create_task(
        self,
        event: str,
        expires_at: datetime,
        /,
        *args: Tuple[Any],
        id: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ):
        self.log.debug(
            f"Creating task for event '{event}' with id '{id}' and expires_at '{expires_at}', args: {args}, kwargs: {kwargs}"
        )
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
            self.log.info(f"Task created with id '{task.id}' for event '{event}'")

        if (
            self._current_task is None
            or task.expires_at < self._current_task.expires_at
        ):
            self._current_task = task
            self._have_data.set()
            self.log.debug(
                f"New task '{task.id}' is now the current task with expires_at '{task.expires_at}'"
            )

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
        await self._have_data.wait()
        task = await self.get_active_task(days)
        return cast(DBTask, task)

    async def dispatch_tasks(self) -> None:
        try:
            while not self.bot.is_closed():
                self.log.debug("Waiting for an active task...")
                task = self._current_task = await self.wait_for_active_task()
                self.log.debug(f"Active task found: {task.id}")
                now = datetime.now(tz=UTC)
                if task.expires_at >= now:
                    sleep_time = (task.expires_at - now).total_seconds()
                    self.log.debug(
                        f"Task '{task.id}' will be dispatched in {sleep_time} seconds."
                    )
                    await asyncio.sleep(sleep_time)

                await self.call_task(task)
        except asyncio.CancelledError:
            self.log.warning("Scheduler dispatch loop cancelled.")
            raise
        except (OSError, discord.ConnectionClosed, asyncpg.PostgresConnectionError):
            self.log.exception("Connection error in dispatch loop, restarting")
            self._task.cancel()
            self._task = asyncio.create_task(self.dispatch_tasks())

    async def call_task(self, task: DBTask):
        self.log.debug(f"Calling task: id={task.id}, event={task.event}")
        async with db_session() as session:
            await session.delete(task)
            await session.commit()
            self.log.info(f"Task '{task.id}' deleted from database.")

        self.bot.dispatch(
            task.event + "_task_completed", *task.extra["args"], **task.extra["kwargs"]
        )
        self.log.debug(
            f"Dispatched event '{task.event}_task_completed' with args: {task.extra['args']} and kwargs: {task.extra['kwargs']}"
        )


setup = Scheduler.setup
