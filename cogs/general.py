from __future__ import annotations
from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands

from data.scrim_config import ScrimConfig
from ui.setup.basic.basic_config_modal import BasicConfigModal


if TYPE_CHECKING:
    from bot import Bot
    from extended_types import GuildInteraction


class General(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        print(f"Loading {self.qualified_name} cog")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        print(f"Unloading {self.qualified_name} cog")
        return await super().cog_unload()

    @app_commands.command()
    async def ping(self, interaction: Interaction):
        """Responds with 'Pong!'"""
        await interaction.response.send_message("Pong!")

    @app_commands.command()
    @app_commands.guild_only()
    async def setup(self, interaction: GuildInteraction):
        scrim_config = ScrimConfig()
        modal = BasicConfigModal(scrim_config=scrim_config)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot):
    await bot.add_cog(General(bot))
