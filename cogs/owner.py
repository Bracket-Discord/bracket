import discord
from core.cog import Cog
from discord.ext import commands

from core.context import GuildContext


class Owner(Cog):
    @commands.is_owner()
    @commands.guild_only()
    @commands.command(name="clean")
    async def clean(self, ctx: GuildContext):
        """Clean up the test server roles and channels."""
        guild = ctx.guild
        for role in guild.roles:
            if role.is_bot_managed() or role.is_default() or role.is_integration():
                continue
            try:
                await role.delete()
            except discord.Forbidden:
                pass

        for channel in guild.channels:
            try:
                await channel.delete()
            except discord.Forbidden:
                pass

        channel = await guild.create_text_channel("test-channel")
        await channel.send("Cleaned up roles and channels in the test server.")


setup = Owner.setup
