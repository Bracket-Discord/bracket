from __future__ import annotations
from typing import TYPE_CHECKING, cast
import discord
from discord.ext import commands
from discord.user import ClientUser
from configs import settings
import uvicorn

import cogs
from core.logger import setup_logger


if TYPE_CHECKING:
    from cogs.scheduler import Scheduler


class BracketBot(commands.Bot):
    def __init__(self):
        self.log = setup_logger("bracketbot")
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=discord.Intents.default(),
        )

    @property
    def scheduler(self) -> Scheduler:
        cog = self.get_cog("Scheduler")
        if cog is None:
            raise RuntimeError("Scheduler cog is not loaded.")
        return cog  # pyright: ignore[reportReturnType]

    async def setup_hook(self):
        await self.load_extension("jishaku")
        self.log.info("Loaded jishaku extension.")

        for ext in cogs.values:
            try:
                await self.load_extension(f"cogs.{ext}")
            except Exception as e:
                self.log.error(f"Failed to load extension {ext}: {e}")

        from backend.app import app

        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8000,
            )
        )

        self.loop.create_task(server.serve())

    async def is_owner(self, user: discord.abc.User, /) -> bool:
        if user.id in settings.owner_ids:
            return True
        return await super().is_owner(user)

    async def on_ready(self):
        user = cast(ClientUser, self.user)
        self.log.info(f"Logged in as {self.user} (ID: {user.id})")
        self.log.info("------")
        if not hasattr(self, "scheduler"):
            self.log.error("Scheduler cog is not loaded. Some features may not work.")


bot = BracketBot()
