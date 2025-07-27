from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Guild, PermissionOverwrite, Role, app_commands, Interaction
from discord.ext import commands

from modals.setup.step1 import SetupStep1


if TYPE_CHECKING:
    from bot import Bot
    from extended_types import GuildInteraction


class General(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    async def ping(self, interaction: Interaction):
        """Responds with 'Pong!'"""
        await interaction.response.send_message("Pong!")

    @app_commands.command()
    @app_commands.guild_only()
    async def setup(self, interaction: GuildInteraction):
        modal = SetupStep1()
        await interaction.response.send_modal(modal)

    async def create_organizer_role(
        self, guild: Guild, name: str = "Organizer"
    ) -> Role:
        role = await guild.create_role(name=name, mentionable=True)
        return role

    async def create_participant_role(
        self, guild: Guild, name: str = "Participant"
    ) -> Role:
        role = await guild.create_role(name=name, mentionable=True)
        return role

    async def create_scrim_channel(self, guild: Guild):

        category = await guild.create_category(
            "Bracket - Tournament",
            overwrites={guild.default_role: PermissionOverwrite(read_messages=False)},
        )
        organizer_role = await self.create_organizer_role(guild)
        channel = await guild.create_text_channel(
            "admin",
            category=category,
            topic="Admin channel for scrims management",
            overwrites={
                organizer_role: PermissionOverwrite(
                    read_messages=True, send_messages=True
                ),
            },
        )


async def setup(bot: Bot):
    await bot.add_cog(General(bot))
    print("General cog loaded successfully.")
