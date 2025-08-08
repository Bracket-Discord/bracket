from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from configs import settings


import cogs


if TYPE_CHECKING:
    from core.context import Context
    from cogs.scheduler import Scheduler


class BracketBot(commands.Bot):
    def __init__(self):
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

    async def print_job(self):
        print("This is a scheduled job running every 5 seconds.")

    async def setup_hook(self):
        await self.load_extension("jishaku")

        for ext in cogs.values:
            try:
                await self.load_extension(f"cogs.{ext}")
            except Exception as e:
                print(f"Failed to load {ext} cog: {e}")

        if settings.default_guild_id:
            print(type(settings.default_guild_id))
            print(f"Syncing commands to guild {settings.default_guild_id}")

    async def is_owner(self, user: discord.abc.User, /) -> bool:
        if user.id in settings.owner_ids:
            return True
        return await super().is_owner(user)

    async def on_ready(self):
        print("Bot is ready!")
        print("------")

    async def on_command_error(self, ctx: Context, error: Exception):  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: {error.param.name}")
            return
        raise error
