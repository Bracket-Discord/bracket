from __future__ import annotations
from typing import TYPE_CHECKING
from discord import  app_commands, Interaction
from discord.ext import commands
from sqlalchemy import select

from db import get_db
from db.models.scrims_channel import ScrimsChannel
from extended_types import GuildInteraction


if TYPE_CHECKING:
    from bot import Bot

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

        async with get_db() as session:
            stmt = select(ScrimsChannel).where(ScrimsChannel.guild_id == interaction.guild.id)
            result = await session.execute(stmt)
        scrim_channel = result.scalar_one_or_none()
        if scrim_channel:
            await interaction.response.send_message("A scrim channel already exists in this guild, delete that first.")
            return

        channel = await interaction.guild.create_text_channel("Bracket")
        async with get_db() as session:
            scrim_channel = ScrimsChannel(
                channel_id=channel.id,
                guild_id=interaction.guild.id
            )
            session.add(scrim_channel)
            await session.commit()

        await interaction.response.send_message(f"Created scrim channel {channel.mention} in this guild.")


async def setup(bot: Bot):
    await bot.add_cog(General(bot))
    print("General cog loaded successfully.")
