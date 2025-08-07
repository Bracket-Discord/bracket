from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands


if TYPE_CHECKING:
    from bot import Bot


class ScrimsCog(commands.Cog, name="Scrims"):
    pass


async def setup(bot: Bot):
    await bot.add_cog(ScrimsCog(bot))
