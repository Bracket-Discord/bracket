from __future__ import annotations
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, cast
import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.sql import func, select
from db.models.guild_config import DBGuildConfig

from core.bracket import BracketBot
from core.cog import Cog
from db import db_session
from db.models.tournament import DBTournament
from db.queries.tournaments import fetch_guild_config, fetch_tournament_by_id
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

    async def tournament_id_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[int]]:
        """Autocomplete for tournament IDs."""
        guild = interaction.guild
        if not guild:
            return []
        stmt = select(DBTournament).where(DBTournament.guild_id == guild.id).limit(10)
        if current != "":
            stmt = stmt.where(
                func.similarity(func.lower(DBTournament.name), func.lower(current))
                > 0.3
            ).order_by(DBTournament.created_at.desc())
        else:
            stmt = stmt.order_by(
                func.similarity(DBTournament.name, current).desc(),
                DBTournament.created_at.desc(),
            )

        async with db_session() as session:
            tournaments = await session.scalars(stmt)

        return [
            app_commands.Choice(
                name=f"{tournament.id} | {tournament.name}", value=tournament.id
            )
            for tournament in tournaments
        ]

    @commands.Cog.listener()
    async def on_open_registration_channel_task_completed(self, tournament_id: int):
        """Open the registration channel for a tournament."""
        print("Opening registration channel for tournament:", tournament_id)
        await self.bot.wait_until_ready()
        tournament = await fetch_tournament_by_id(tournament_id)
        if not tournament:
            print(f"Tournament with ID {tournament_id} not found.")
            return
        guild = self.bot.get_guild(tournament.guild_id)
        print("Opening registration channel for tournament:", tournament.name)
        if not guild:
            print("Guild not found for tournament:", tournament.name)
            return
        registration_channel = guild.get_channel(tournament.registration_channel_id)
        if not registration_channel:
            print(
                f"Registration channel not found for tournament {tournament.name} "
                f"in guild {guild.name}."
            )
            return

        await registration_channel.set_permissions(
            guild.default_role,
            read_messages=True,
            send_messages=True,
        )

        logs_channel = cast(
            discord.TextChannel, guild.get_channel(tournament.logs_channel_id)
        )
        if logs_channel:
            print(
                f"Sending registration open message to logs channel: {logs_channel.name}"
            )
            await logs_channel.send(
                f"Registration for the tournament '{tournament.name}' is now open! "
                f"Please check {registration_channel.mention} for details."
            )

    @commands.hybrid_command(name="delete")
    @commands.guild_only()
    @commands.check(can_create_tournament)
    @commands.bot_has_permissions(manage_channels=True, manage_roles=True)
    @app_commands.describe(id="The ID of the tournament to delete")
    @app_commands.autocomplete(id=tournament_id_autocomplete)
    async def delete(self, ctx: GuildContext, *, id: int):
        """Delete a tournament by name."""
        guild = ctx.guild
        tournament = await fetch_tournament_by_id(id)
        if not tournament or tournament.guild_id != guild.id:
            await ctx.reply(
                "Tournament not found or you do not have permission to delete it."
            )
            return
        # TODO: Don't allow deletion of tournaments with ongoing matches or registrations
        await ctx.defer()
        channel_ids = [
            tournament.admin_channel_id,
            tournament.registration_channel_id,
            tournament.logs_channel_id,
            tournament.category_id,
        ]

        for channel_id in channel_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    await channel.delete(
                        reason=f"Deleting tournament channels. Action By {ctx.author}"
                    )
                except discord.Forbidden:
                    await ctx.reply(
                        f"Failed to delete channel {channel.mention}. "
                        "Please check my permissions."
                    )
                    return

        async with db_session() as session:
            await session.delete(tournament)
            await session.commit()

        await ctx.reply(
            f"Tournament '{tournament.name}' deleted successfully! "
            "All associated channels have been removed."
        )

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
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                admin_role: discord.PermissionOverwrite(read_messages=True),
            },
        )
        admin_channel = await guild.create_text_channel(
            name="admin",
            reason="Creating an admin channel for the tournament.",
            topic=f"Admin channel for the {name} tournament.",
            category=category_channel,
        )
        logs_channel = await guild.create_text_channel(
            name="logs",
            reason="Creating a logs channel for the tournament.",
            topic=f"Logs channel for the {name} tournament.",
            category=category_channel,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                admin_role: discord.PermissionOverwrite(read_messages=True),
            },
        )
        registration_channel = await guild.create_text_channel(
            name="registration",
            reason="Creating a registration channel for the tournament.",
            topic=f"Registration channel for the {name} tournament.",
            category=category_channel,
            overwrites={
                # Keep everyone not see messages until registration is open
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                admin_role: discord.PermissionOverwrite(
                    read_messages=True, send_messages=True
                ),
            },
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

        expire_time = datetime.now(UTC) + timedelta(seconds=10)
        await self.bot.scheduler.create_task(
            "open_registration_channel",
            expire_time,
            tournament.id,
        )
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
