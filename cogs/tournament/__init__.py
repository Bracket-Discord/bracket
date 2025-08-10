from __future__ import annotations
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, cast
import discord
from discord import app_commands
from sqlalchemy.sql import func, select
from cogs.tournament.invite_member_view import InviteMemberView
from core.logger import setup_logger
from db.models.guild_config import DBGuildConfig

from core.bracket import BracketBot
from core.cog import Cog
from db import db_session
from db.models.tournament import DBTournament
from db.queries.tournaments import (
    create_team,
    fetch_guild_config,
    fetch_team_by_id,
    fetch_tournament_by_id,
)
from ui.view.confirm import Confirm
from utils.interaction import send_message

if TYPE_CHECKING:
    from core.interaction import GuildInteraction


async def can_create_tournament(interaction: GuildInteraction) -> bool:
    """Check if the user can create a tournament."""
    guild = interaction.guild
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
    return (
        admin_role in interaction.user.roles
        or interaction.user.guild_permissions.manage_guild
    )


class TournamentCog(Cog, name="Tournament"):
    """Cog for managing tournaments."""

    def __init__(self, bot: BracketBot):
        self.bot = bot
        self.log = setup_logger("tournament")

    team = app_commands.Group(
        name="team",
        description="Manage teams for tournaments.",
        guild_only=True,
    )

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

    @Cog.listener()
    async def on_open_registration_channel_task_completed(self, tournament_id: int):
        """Open the registration channel for a tournament."""
        await self.bot.wait_until_ready()
        tournament = await fetch_tournament_by_id(tournament_id)
        if not tournament:
            self.log.warning(f"Tournament with ID {tournament_id} not found.")
            return
        guild = self.bot.get_guild(tournament.guild_id)
        if not guild:
            return
        registration_channel = guild.get_channel(tournament.registration_channel_id)
        if not registration_channel:
            return

        await registration_channel.set_permissions(
            guild.default_role,
            read_messages=True,
            send_messages=True,
        )
        self.log.info(
            f"Opened registration channel for tournament '{tournament.name}' "
            f"in guild '{guild.name}' ({guild.id})."
        )

        logs_channel = cast(
            discord.TextChannel, guild.get_channel(tournament.logs_channel_id)
        )

        if logs_channel:
            await logs_channel.send(
                f"Registration for the tournament '{tournament.name}' is now open! "
                f"Please check {registration_channel.mention} for details."
            )
        else:
            self.log.warning(
                f"Logs channel for tournament {tournament.name} not found. "
                "Cannot send registration open message."
            )

    @app_commands.command(name="delete")
    @app_commands.guild_only()
    @app_commands.check(can_create_tournament)
    @app_commands.describe(id="The ID of the tournament to delete")
    @app_commands.autocomplete(id=tournament_id_autocomplete)
    async def delete(self, interaction: GuildInteraction, *, id: int):
        """Delete a tournament by name."""
        guild = interaction.guild
        tournament = await fetch_tournament_by_id(id)
        if not tournament or tournament.guild_id != guild.id:
            await interaction.response.send_message(
                "Tournament not found or you do not have permission to delete it."
            )
            return
        # TODO: Don't allow deletion of tournaments with ongoing matches or registrations
        await interaction.response.defer()
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
                        reason=f"Deleting tournament channels. Action By {interaction.user}"
                    )
                except discord.Forbidden:
                    self.log.warning(
                        f"Failed to delete channel {channel.name} ({channel.id}) "
                        f"in guild {guild.name} ({guild.id}). "
                        "Check my permissions."
                    )
                    await interaction.response.send_message(
                        f"Failed to delete channel {channel.mention}. "
                        "Please check my permissions."
                    )
                    return

        async with db_session() as session:
            await session.delete(tournament)
            await session.commit()

        await interaction.response.send_message(
            f"Tournament '{tournament.name}' deleted successfully! "
            "All associated channels have been removed."
        )

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.check(can_create_tournament)
    async def create(self, interaction: GuildInteraction, *, name: str):
        """Create a new tournament."""
        guild = interaction.guild
        guild_config = await fetch_guild_config(guild.id)
        if not guild_config:
            await interaction.response.send_message(
                "No configuration found for this guild. Please create one using `/setup`."
            )
            return
        admin_role = (
            guild.get_role(guild_config.admin_role_id)
            if guild_config.admin_role_id
            else None
        )
        if not admin_role:
            await interaction.response.send_message(
                "No admin role configured for this guild."
                " Please set it up first. Use `/setup` to configure the tournament system."
            )
            return

        self.log.debug(
            f"Creating tournament '{name}' in guild '{guild.name}' with admin role '{admin_role.name}'"
        )
        self.log.debug(f"Creating category `{name} Tournament` in guild '{guild.id}'")
        category_channel = await guild.create_category(
            name=f"{name} Tournament",
            reason="Creating a category for the new tournament.",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                admin_role: discord.PermissionOverwrite(read_messages=True),
            },
        )
        self.log.debug(
            f"Creating admin channel in category '{category_channel.name}' for guild '{guild.id}'"
        )
        admin_channel = await guild.create_text_channel(
            name="admin",
            reason="Creating an admin channel for the tournament.",
            topic=f"Admin channel for the {name} tournament.",
            category=category_channel,
        )
        self.log.debug(
            f"Creating logs channel in category '{category_channel.name}' for guild '{guild.id}'"
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
        self.log.debug(
            f"Creating registration channel in category '{category_channel.name}' for guild '{guild.id}'"
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
        self.log.debug(
            f"Creating tournament '{name}' in database for guild '{guild.id}'"
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

        self.log.debug(
            f"Scheduling task to open registration channel for tournament '{name}'"
        )
        expire_time = datetime.now(UTC) + timedelta(seconds=10)
        await self.bot.scheduler.create_task(
            "open_registration_channel",
            expire_time,
            tournament.id,
        )
        self.log.info(f"Tournament '{name}' created successfully in guild '{guild.id}'")
        await interaction.response.send_message(
            f"Tournament '{name}' created successfully! "
            f"You can manage it in {admin_channel.mention}:\n"
        )

    @app_commands.command(name="setup")
    @app_commands.guild_only()
    async def _setup(self, interaction: GuildInteraction):
        """Setup the tournament system for this guild."""
        guild = interaction.guild
        guild_config = await fetch_guild_config(guild.id)
        admin_role = None
        if guild_config:
            admin_role = guild.get_role(guild_config.admin_role_id)
            if not admin_role:
                confirm = Confirm(user_id=interaction.user.id)
                await send_message(
                    "We can't find the admin role, do you want to set it up again? ",
                    interaction=interaction,
                    view=confirm,
                )
                await confirm.wait()
                if confirm.value is None:
                    await send_message(
                        "Setup timed out. Please try again later.",
                        interaction=interaction,
                        ephemeral=True,
                    )
                    return
                if not confirm.value:
                    await send_message(
                        "Setup cancelled. You can try again later.",
                        interaction=interaction,
                        ephemeral=True,
                    )
                    return
        if not admin_role:
            admin_role = await guild.create_role(
                name="Tournament Admin",
                mentionable=True,
                reason="Creating a role for tournament administration.",
            )
        else:
            await send_message(
                f"Admin role already exists: {admin_role.mention}. "
                "You can change it later if needed.",
                interaction=interaction,
                ephemeral=True,
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

        content = (
            f"Setup complete! Admin role is now set to: {admin_role.mention}. "
            "You can now create tournaments using `/create`."
        )
        await send_message(content, interaction=interaction, ephemeral=True)

    @team.command(name="create")
    @app_commands.guild_only()
    async def create_team(self, interaction: GuildInteraction, *, name: str):
        team = await create_team(name, interaction.user.id)
        await interaction.response.send_message(
            f"Team '{team.name}' created successfully! "
            f"Your team ID is {team.id}. You can now register for tournaments."
        )

    @team.command(name="invite")
    @app_commands.guild_only()
    async def invite_member(self, interaction: GuildInteraction, team_id: int):
        """Invite a member to your team."""
        team = await fetch_team_by_id(team_id)
        if not team or team.captain_id != interaction.user.id:
            await send_message(
                "You do not have permission to invite members to this team.",
                interaction=interaction,
            )
            return

        view = InviteMemberView()
        await send_message(
            "Please select a user to invite to your team:",
            view=view,
            ephemeral=True,
            interaction=interaction,
        )
        await view.wait()
        if not view.users:
            await send_message(
                "No users selected. Invite cancelled.",
                interaction=interaction,
                ephemeral=True,
            )
            return
        invited_users: list[discord.User | discord.Member] = []
        for user in view.users:
            if user.id == interaction.user.id:
                continue
            invited_users.append(user)
        if not invited_users:
            await send_message(
                "You cannot invite yourself. Invite cancelled.",
                interaction=interaction,
                ephemeral=True,
            )
            return
        for user in invited_users:
            with suppress(discord.Forbidden):
                await user.send(
                    f"You have been invited to join the team '{team.name}' in the tournament. "
                    f"To accept, please use the command `/team join {team.id}`."
                )
        await send_message(
            f"You have invited {', '.join(user.mention for user in invited_users)} to your team '{team.name}'.",
            interaction=interaction,
        )


setup = TournamentCog.setup
