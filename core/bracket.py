from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from configs import settings


import cogs

if TYPE_CHECKING:
    from core.context import Context


class BracketBot(commands.Bot):
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
            # await bot.tree.sync(guild=discord.Object(id=settings.default_guild_id))

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
