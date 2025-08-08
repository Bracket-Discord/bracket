from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands

if TYPE_CHECKING:
    from core.bracket import BracketBot


class Cog(commands.Cog):
    def __init__(self, bot: BracketBot):
        self.bot = bot

    async def cog_load(self):
        """Called when the cog is loaded."""
        print(f"Loaded cog: {self.qualified_name}")

    async def cog_unload(self):
        """Called when the cog is unloaded."""
        print(f"Unloaded cog: {self.qualified_name}")

    @classmethod
    async def setup(cls, bot: BracketBot):
        """Setup function to add the cog to the bot."""
        await bot.add_cog(cls(bot))
        print(f"Cog {cls.__name__} has been set up.")
