from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from db.models.guild_config import DBGuildConfig

from core.bracket import BracketBot
from core.cog import Cog
from db import db_session
from db.models.tournament import DBTournament
from db.queries.tournaments import fetch_guild_config
from ui.view.confirm import Confirm

if TYPE_CHECKING:
    from core.context import GuildContext


async def can_create_tournament(ctx: GuildContext) -> bool:
    """Check if the user can create a tournament."""
    guild = ctx.guild
    guild_config = await fetch_guild_config(guild.id)
    if not guild_config:
        return False
    admin_role = (
        guild.get_role(guild_config.admin_role_id)
        if guild_config.admin_role_id
        else None
    )
    if not admin_role:
        return False
    return admin_role in ctx.author.roles or ctx.author.guild_permissions.manage_guild


class TournamentCog(Cog, name="Tournament"):
    """Cog for managing tournaments."""

    def __init__(self, bot: BracketBot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(can_create_tournament)
    async def create(self, ctx: GuildContext, *, name: str):
        """Create a new tournament."""
        guild = ctx.guild
        guild_config = await fetch_guild_config(guild.id)
        if not guild_config:
            await ctx.reply(
                "No configuration found for this guild. Please create one using `/setup`."
            )
            return
        admin_role = (
            guild.get_role(guild_config.admin_role_id)
            if guild_config.admin_role_id
            else None
        )
        if not admin_role:
            await ctx.reply(
                "No admin role configured for this guild."
                " Please set it up first. Use `/setup` to configure the tournament system."
            )
            return

        category_channel = await guild.create_category(
            name=f"{name} Tournament",
            reason="Creating a category for the new tournament.",
        )
        admin_channel = await category_channel.create_text_channel(
            name="admin",
            reason="Creating an admin channel for the tournament.",
            topic=f"Admin channel for the {name} tournament.",
        )
        logs_channel = await category_channel.create_text_channel(
            name="logs",
            reason="Creating a logs channel for the tournament.",
            topic=f"Logs channel for the {name} tournament.",
        )
        registration_channel = await category_channel.create_text_channel(
            name="registration",
            reason="Creating a registration channel for the tournament.",
            topic=f"Registration channel for the {name} tournament.",
        )
        async with db_session() as session:
            tournament = DBTournament(
                guild_id=guild.id,
                name=name,
                category_id=category_channel.id,
                admin_channel_id=admin_channel.id,
                registration_channel_id=registration_channel.id,
                logs_channel_id=logs_channel.id,
            )
            session.add(tournament)
            await session.commit()

        await ctx.reply(
            f"Tournament '{name}' created successfully! "
            f"You can manage it in {admin_channel.mention}:\n"
        )

    @commands.hybrid_command(name="setup")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _setup(self, ctx: GuildContext):
        """Setup the tournament system for this guild."""
        guild = ctx.guild
        guild_config = await fetch_guild_config(guild.id)
        admin_role = None
        if guild_config:
            admin_role = guild.get_role(guild_config.admin_role_id)
            if not admin_role:
                confirm = Confirm(user_id=ctx.author.id)
                await ctx.reply(
                    "We can't find the admin role, do you want to set it up again? ",
                    view=confirm,
                )
                await confirm.wait()
                if confirm.value is None:
                    await ctx.reply("Timeout, please try again.")
                    return
                if not confirm.value:
                    await ctx.reply("Setup cancelled.")
                    return
        if not admin_role:
            admin_role = await guild.create_role(
                name="Tournament Admin",
                mentionable=True,
                reason="Creating a role for tournament administration.",
            )
        else:
            await ctx.reply(
                f"Admin role already exists: {admin_role.mention}. "
                "You can change it later if needed.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return
        async with db_session() as session:
            if not guild_config:
                guild_config = DBGuildConfig(
                    guild_id=guild.id, admin_role_id=admin_role.id
                )
            else:
                guild_config.admin_role_id = admin_role.id

            session.add(guild_config)
            await session.commit()

        await ctx.reply(
            f"Setup complete! Admin role is now set to: {admin_role.mention}. "
            "You can now create tournaments using `/create`."
        )


setup = TournamentCog.setup
