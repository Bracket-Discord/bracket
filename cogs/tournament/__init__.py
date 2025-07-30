from __future__ import annotations
from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING, List, Self, cast
from discord import app_commands
import discord
from discord.ext import commands
from sqlalchemy import func, select, text
from sqlalchemy.sql.functions import count

from cogs.tournament.config import BestOf, BracketType, ScrimConfig, TournamentType
from cogs.tournament.embeds import ScrimConfigEmbed
from db import get_db
from utils import generate_random_string


if TYPE_CHECKING:
    from bot import Bot
    from extended_types import GuildInteraction
    from db.models.scrim import Scrim


class BasicConfigModal(discord.ui.Modal, title="Create Tournament"):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config
        self.name.default = scrim_config.scrim_name
        self.organizer_role.default = scrim_config.organizer_role_name
        self.participant_role.default = scrim_config.participant_role_name

    name = discord.ui.TextInput[Self](
        label="Tournament Name",
        placeholder="Enter the name of the scrim",
        required=True,
        max_length=100,
        min_length=1,
    )
    organizer_role = discord.ui.TextInput[Self](
        label="Organizer Role",
        placeholder="Enter the name of the organizer role",
        min_length=3,
        max_length=50,
        default="Organizer",
    )
    participant_role = discord.ui.TextInput[Self](
        label="Participant Role",
        placeholder="Enter the name of the participant role",
        min_length=3,
        max_length=50,
        default="Participant",
    )

    async def on_submit(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, interaction: GuildInteraction
    ) -> None:
        scrim_config = self.scrim_config
        scrim_config.scrim_name = self.name.value
        scrim_config.organizer_role_name = self.organizer_role.value
        scrim_config.participant_role_name = self.participant_role.value

        await interaction.response.send_message(
            embed=ScrimConfigEmbed(scrim_config),
            view=TournamentTypeView(scrim_config),
            ephemeral=True,
        )


class TournamentTypeView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    def _update_buttons(self):
        if self.scrim_config.tournament_type:
            self.proceed_to_bracket.disabled = False

    @discord.ui.button(label="Solo", style=discord.ButtonStyle.primary)
    async def solo_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.tournament_type = TournamentType.SOLO
        self._update_buttons()
        await interaction.response.edit_message(
            view=self, embed=ScrimConfigEmbed(self.scrim_config)
        )

    @discord.ui.button(label="Duo", style=discord.ButtonStyle.primary)
    async def duo_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.tournament_type = TournamentType.DUO
        self._update_buttons()
        await interaction.response.edit_message(
            view=self, embed=ScrimConfigEmbed(self.scrim_config)
        )

    @discord.ui.button(label="Team", style=discord.ButtonStyle.primary)
    async def team_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.tournament_type = TournamentType.TEAM
        self._update_buttons()
        await interaction.response.edit_message(
            view=self, embed=ScrimConfigEmbed(self.scrim_config)
        )

    @discord.ui.button(
        label="Configure Format and Bracket",
        style=discord.ButtonStyle.success,
        disabled=True,
    )
    async def proceed_to_bracket(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        await interaction.response.edit_message(
            embed=ScrimConfigEmbed(self.scrim_config),
            view=BracketConfigView(self.scrim_config),
        )


class BracketConfigView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    def _update_buttons(self):
        if self.scrim_config.bracket_type:
            self.proceed_to_bestof.disabled = False

    @discord.ui.button(label="Single Elimination", style=discord.ButtonStyle.primary)
    async def single_elimination_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.bracket_type = BracketType.SINGLE_ELIMINATION
        self._update_buttons()
        await interaction.response.edit_message(
            view=self,
            embed=ScrimConfigEmbed(self.scrim_config),
        )

    @discord.ui.button(label="Double Elimination", style=discord.ButtonStyle.primary)
    async def double_elimination_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.bracket_type = BracketType.DOUBLE_ELIMINATION
        self._update_buttons()
        await interaction.response.edit_message(
            view=self,
            embed=ScrimConfigEmbed(self.scrim_config),
        )

    @discord.ui.button(label="Round Robin", style=discord.ButtonStyle.primary)
    async def round_robin_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.bracket_type = BracketType.ROUND_ROBIN
        self._update_buttons()
        await interaction.response.edit_message(
            view=self,
            embed=ScrimConfigEmbed(self.scrim_config),
        )

    @discord.ui.button(label="Swiss", style=discord.ButtonStyle.primary)
    async def swiss_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.bracket_type = BracketType.SWISS
        self._update_buttons()
        await interaction.response.edit_message(
            view=self,
            embed=ScrimConfigEmbed(self.scrim_config),
        )

    @discord.ui.button(
        label="Proceed to Best of Configuration",
        style=discord.ButtonStyle.success,
        disabled=True,
    )
    async def proceed_to_bestof(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        await interaction.response.edit_message(
            embed=ScrimConfigEmbed(self.scrim_config),
            view=BestOfConfigView(self.scrim_config),
        )


class BestOfConfigView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    def _update_buttons(self):
        if self.scrim_config.best_of:
            self.proceed_to_timing.disabled = False

    @discord.ui.button(label="Best of 1", style=discord.ButtonStyle.primary)
    async def bo1_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.best_of = BestOf.BO1
        self._update_buttons()
        await interaction.response.edit_message(
            view=self, embed=ScrimConfigEmbed(self.scrim_config)
        )

    @discord.ui.button(label="Best of 3", style=discord.ButtonStyle.primary)
    async def bo3_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.best_of = BestOf.BO3
        self._update_buttons()
        await interaction.response.edit_message(
            view=self, embed=ScrimConfigEmbed(self.scrim_config)
        )

    @discord.ui.button(label="Best of 5", style=discord.ButtonStyle.primary)
    async def bo5_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        self.scrim_config.best_of = BestOf.BO5
        self._update_buttons()
        await interaction.response.edit_message(
            view=self,
            embed=ScrimConfigEmbed(self.scrim_config),
        )

    @discord.ui.button(
        label="Proceed to Timing Configuration",
        style=discord.ButtonStyle.success,
        disabled=True,
    )
    async def proceed_to_timing(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        timing_modal = TimingConfigModal(self.scrim_config)
        timing_modal.update_default_values()
        await interaction.response.send_modal(timing_modal)


class TimingConfigRetryView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__()
        self.scrim_config = scrim_config

    @discord.ui.button(label="Retry", style=discord.ButtonStyle.green)
    async def retry_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        timing_modal = TimingConfigModal(self.scrim_config)
        timing_modal.update_default_values()
        await interaction.response.send_modal(timing_modal)


class TimingConfigModal(discord.ui.Modal, title="Scrim Timing Configuration"):
    def __init__(self, scrim_config: ScrimConfig) -> None:
        super().__init__()
        self.scrim_config = scrim_config
        self.update_default_values()

    def update_default_values(self) -> None:
        """Update the default values of the text inputs."""
        self.date.default = self.scrim_config.date_input
        self.time.default = self.scrim_config.time_input

    date = discord.ui.TextInput[Self](
        label="Scrim Date (YYYY-MM-DD)",
        placeholder="Enter the date of the scrim (YYYY-MM-DD)",
        required=True,
        max_length=10,
    )
    time = discord.ui.TextInput[Self](
        label="Scrim Time (HH:MM)",
        placeholder="Enter the time of the scrim (HH:MM)",
        required=True,
        max_length=5,
    )

    async def on_submit(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, interaction: GuildInteraction
    ) -> None:
        self.scrim_config.date_input = self.date.value
        self.scrim_config.time_input = self.time.value
        self.update_default_values()
        retry_view = TimingConfigRetryView(self.scrim_config)

        try:
            datetime.strptime(self.date.value, "%Y-%m-%d").date()
        except ValueError:
            embed = discord.Embed(
                title="Invalid Date Format",
                description=(
                    f"❌ You entered: `{self.date.value}`\n\n"
                    "Please enter the date in **YYYY-MM-DD** format.\n"
                    "Example: `2025-07-30`"
                ),
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True, view=retry_view
            )
            return

        try:
            datetime.strptime(self.time.value, "%H:%M").time()
        except ValueError:
            embed = discord.Embed(
                title="Invalid Time Format",
                description=(
                    f"❌ You entered: `{self.time.value}`\n\n"
                    "Please enter the time in **HH:MM** format.\n"
                    "Example: `14:30`"
                ),
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True, view=retry_view
            )
            return

        await interaction.response.edit_message(
            view=ProceedToTournamentInfoView(self.scrim_config),
            embed=ScrimConfigEmbed(self.scrim_config),
        )


class ProceedToTournamentInfoView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    @discord.ui.button(
        label="Set Rules and Description", style=discord.ButtonStyle.primary
    )
    async def edit_info_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        modal = TournamentInfoModal(self.scrim_config)
        modal.update_scrim_config()
        await interaction.response.send_modal(modal)


class TournamentConfigRetryView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__()
        self.scrim_config = scrim_config

    @discord.ui.button(label="Retry", style=discord.ButtonStyle.green)
    async def retry_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        tournament_model = TournamentInfoModal(self.scrim_config)
        tournament_model.update_scrim_config()
        await interaction.response.send_modal(tournament_model)


class TournamentInfoModal(discord.ui.Modal, title="Tournament Info"):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__()
        self.scrim_config = scrim_config
        self.update_scrim_config()

    def update_scrim_config(self) -> None:
        self.teamcap.default = str(self.scrim_config.teamcap)
        self.rules.default = self.scrim_config.rules or ""
        self.description.default = self.scrim_config.description or ""

        items = [
            self.teamcap,
            self.prize,
            self.rules,
            self.description,
        ]
        self.clear_items()
        for item in items:
            if (
                item == self.teamcap
                and self.scrim_config.tournament_type != TournamentType.TEAM
            ):
                continue
            self.add_item(item)

    prize = discord.ui.TextInput[Self](
        label="Scrim Prize",
        placeholder="Enter the prize for the scrim ",
        required=False,
        max_length=50,
    )
    teamcap = discord.ui.TextInput[Self](
        label="Team Cap",
        placeholder="Enter the maximum number of teams allowed",
        required=True,
        max_length=2,
    )
    rules = discord.ui.TextInput[Self](
        label="Scrim Rules",
        placeholder="Enter the rules for the scrim",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph,
    )
    description = discord.ui.TextInput[Self](
        label="Scrim Description",
        placeholder="Enter a brief description of the scrim",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph,
    )

    async def on_submit(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, interaction: GuildInteraction
    ) -> None:
        retry_view = TournamentConfigRetryView(self.scrim_config)
        config = self.scrim_config
        try:
            if self.scrim_config.tournament_type == TournamentType.TEAM:
                try:
                    config.teamcap = int(self.teamcap.value)
                except ValueError:
                    raise ValueError("Team cap must be a valid integer.")
                if config.teamcap < 3:
                    raise ValueError("Team cap must be at least 3 or higher.")
                elif config.teamcap > 10:
                    raise ValueError("Team cap must not exceed 10.")

        except ValueError as e:
            embed = discord.Embed(
                title="Invalid Team Cap",
                description=(
                    f"❌ You entered: `{self.teamcap.value}`\n\n" + str(e) + "\n\n"
                ),
                color=discord.Color.red(),
            )
            await interaction.response.edit_message(embed=embed, view=retry_view)
            return

        config.description = self.description.value
        config.rules = self.rules.value

        self.update_scrim_config()

        await interaction.response.edit_message(
            embed=ScrimConfigEmbed(self.scrim_config),
            view=ConfirmView(self.scrim_config),
        )


class ConfirmView(discord.ui.View):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    @discord.ui.button(
        label="Confirm Tournament Setup", style=discord.ButtonStyle.success
    )
    async def confirm_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        await interaction.response.defer(thinking=True)
        from db.models.scrim import Scrim

        scrim_entry = Scrim(
            name=self.scrim_config.scrim_name,
            guild_id=interaction.guild.id,
            best_of=self.scrim_config.best_of,
            max_team_size=self.scrim_config.max_team_size,
            teamcap=self.scrim_config.teamcap,
            tournament_type=self.scrim_config.tournament_type,
            bracket_type=self.scrim_config.bracket_type,
            prize=self.scrim_config.prize,
            rules=self.scrim_config.rules,
            description=self.scrim_config.description,
            time=datetime.strptime(
                f"{self.scrim_config.date_input} {self.scrim_config.time_input}",
                "%Y-%m-%d %H:%M",
            ),
        )
        embed = ScrimConfigEmbed(self.scrim_config)
        embed.set_footer(text="Tournament setup complete!")
        await self.create_roles(interaction.guild, scrim_entry)
        await self.create_channels(interaction.guild, scrim_entry)
        async with get_db() as session:
            session.add(scrim_entry)
            await session.commit()
        await interaction.edit_original_response(embed=embed, view=None)

    async def create_roles(self, guild: discord.Guild, scrim_entry: Scrim):
        """Create the organizer and participant roles in the guild."""
        organizer_role = await guild.create_role(
            name=self.scrim_config.organizer_role_name
        )
        participant_role = await guild.create_role(
            name=self.scrim_config.participant_role_name
        )
        scrim_entry.organizer_role_id = organizer_role.id
        scrim_entry.participant_role_id = participant_role.id

    async def create_channels(self, guild: discord.Guild, scrim_entry: Scrim):
        """Create a channel for the scrim."""
        category = await guild.create_category(
            name=f"{scrim_entry.name} - Tournament",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                discord.Object(
                    scrim_entry.organizer_role_id
                ): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            },
        )
        admin_channel = await guild.create_text_channel(
            name="admin",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                discord.Object(
                    scrim_entry.organizer_role_id
                ): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            },
        )
        logs_channel = await guild.create_text_channel(
            name="logs",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                discord.Object(
                    scrim_entry.organizer_role_id
                ): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            },
        )
        register_channel = await guild.create_text_channel(
            name="register",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            },
        )
        annoucement_channel = await guild.create_text_channel(
            name="announcements",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            },
        )
        scrim_entry.admin_channel_id = admin_channel.id
        scrim_entry.logs_channel_id = logs_channel.id
        scrim_entry.register_channel_id = register_channel.id
        scrim_entry.announcements_channel_id = annoucement_channel.id
        scrim_entry.category_id = category.id


class Tournament(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    team_group = app_commands.Group(
        name="team", description="Manage your teams in tournaments"
    )

    async def get_unique_secret(self) -> str:
        """Generate a unique secret for the team."""
        from db.models.team import Team

        while True:
            secret = generate_random_string(16)
            async with get_db() as session:
                stmt = select(1).where(func.lower(Team.secret) == secret.lower())
                result = await session.execute(stmt)
                if not result.scalar_one_or_none():
                    return secret

    @app_commands.command()
    @app_commands.guild_only()
    async def setup(self, interaction: GuildInteraction):
        scrim_config = ScrimConfig()
        modal = BasicConfigModal(scrim_config=scrim_config)
        await interaction.response.send_modal(modal)

    async def tournament_id_autocomplete(
        self, interaction: GuildInteraction, current: str
    ) -> List[app_commands.Choice[int]]:
        from db.models import Scrim

        stmt = (
            select(Scrim)
            .where(Scrim.guild_id == interaction.guild.id)
            .order_by(func.similarity(Scrim.name, current).desc())
            .order_by(Scrim.id.desc())
            .limit(10)
        )

        if current:
            stmt = stmt.where(
                func.similarity(func.lower(Scrim.name), current.lower()) > 0.3
            )

        async with get_db() as session:
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
            await session.commit()

        async with get_db() as session:
            result = await session.execute(stmt)
            scrims = result.scalars().all()

        return [
            app_commands.Choice(name=f"{scrim.id} - {scrim.name}", value=scrim.id)
            for scrim in scrims
        ]

    @app_commands.command(name="delete")
    @app_commands.guild_only()
    @app_commands.rename(tournament_id="tournament")
    @app_commands.autocomplete(tournament_id=tournament_id_autocomplete)
    async def delete_tournament(
        self, interaction: GuildInteraction, tournament_id: int
    ):
        from db.models.scrim import Scrim

        async with get_db() as session:
            stmt = select(Scrim).where(
                Scrim.id == tournament_id, Scrim.guild_id == interaction.guild.id
            )
            result = await session.execute(stmt)
            scrim = result.scalar_one_or_none()

        if not scrim:
            await interaction.response.send_message(
                "No tournament found with that ID in this server.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        roles_ids = [
            scrim.organizer_role_id,
            scrim.participant_role_id,
        ]

        for role_id in roles_ids:
            role = guild.get_role(role_id)
            if role:
                try:
                    await role.delete()
                except discord.Forbidden:
                    print(f"Failed to delete role {role.name} (ID: {role.id})")
                except discord.HTTPException as e:
                    print(f"Error deleting role {role.name}: {e}")

        channels_ids = [
            scrim.category_id,
            scrim.admin_channel_id,
            scrim.logs_channel_id,
            scrim.register_channel_id,
            scrim.announcements_channel_id,
        ]

        for channel_id in channels_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                try:
                    await channel.delete()
                except discord.Forbidden:
                    print(f"Failed to delete channel {channel.name} (ID: {channel.id})")
                except discord.HTTPException as e:
                    print(f"Error deleting channel {channel.name}: {e}")

        async with get_db() as session:
            await session.delete(scrim)
            await session.commit()

        await interaction.edit_original_response(
            content="Tournament deleted successfully."
        )

    @app_commands.guild_only()
    @app_commands.describe(team_name="The name of the team you want to create")
    @app_commands.rename(team_name="name")
    @team_group.command(
        name="create",
    )
    async def create_team(self, interaction: GuildInteraction, team_name: str):
        from db.models.team import Team, TeamMember
        from db.models.scrim import Scrim

        # TODO: Make helper database function to do repetitive tasks like this
        async with get_db() as session:
            stmt = select(Scrim).where(
                Scrim.register_channel_id == interaction.channel_id
            )
            result = await session.execute(stmt)
            scrim = result.scalar_one_or_none()

        if not scrim:
            await interaction.response.send_message(
                "This channel is not a valid tournament registration channel.",
                ephemeral=True,
            )
            return

        async with get_db() as session:
            stmt = select(1).where(
                func.lower(Team.name) == team_name.lower(),
                Team.scrim_id == scrim.id,
            )

            result = await session.execute(stmt)
            team_exists_with_same_name = result.scalar_one_or_none() is not None

        if team_exists_with_same_name:
            await interaction.response.send_message(
                f"A team with the name `{team_name}` already exists in this tournament."
                " Consider using a different name."
                " We have to do this to prevent confusion.",
                ephemeral=True,
            )
            return

        # Check if same user is already a captain in this tournament
        async with get_db() as session:
            stmt = select(Team).where(
                Team.captain_id == interaction.user.id, Team.scrim_id == scrim.id
            )
            existing_team = (await session.execute(stmt)).scalar_one_or_none()

        if existing_team:
            await interaction.response.send_message(
                f"You are already a captain of the team `{existing_team.name}` in this tournament.",
                ephemeral=True,
            )
            return

        # TODO: Check if user is a participant in this tournament, maybe a captain or a member of a team
        async with get_db() as session:
            stmt = select(1).where(
                TeamMember.user_id == interaction.user.id,
                TeamMember.scrim_id == scrim.id,
            )
            result = await session.execute(stmt)
            is_participant = result.scalar_one_or_none() is not None

        if is_participant:
            await interaction.response.send_message(
                "You are already a participant in this tournament. "
                "You can create a team or join an existing one.",
                ephemeral=True,
            )
            return

        secret = await self.get_unique_secret()

        async with get_db() as session:
            team = Team(
                name=team_name,
                captain_id=interaction.user.id,
                scrim_id=scrim.id,
                secret=secret,
                max_size=scrim.max_team_size,
            )
            session.add(team)
            await session.flush()
            team_member = TeamMember(
                team_id=team.id,
                user_id=interaction.user.id,
                scrim_id=scrim.id,
            )
            session.add(team_member)
            await session.commit()

        message = (
            f"Team `{team_name}` registerd successfully! "
            f"Players can join your team using `/team join {secret}`"
        )
        await interaction.response.send_message(
            message,
            ephemeral=True,
        )

        with suppress(discord.HTTPException):
            channel = cast(discord.TextChannel, interaction.channel)
            await channel.send(
                f"Team `{team_name}` has been created by {interaction.user.mention}!"
            )

        with suppress(discord.HTTPException):
            await interaction.user.send(message)

    @team_group.command(name="join")
    @app_commands.guild_only()
    @app_commands.describe(
        code="Code provided by the team captain",
    )
    async def join_team(self, interaction: GuildInteraction, code: str):
        from db.models.team import Team, TeamMember
        from db.models.scrim import Scrim

        async with get_db() as session:
            stmt = select(Scrim).where(
                Scrim.register_channel_id == interaction.channel_id
            )
            result = await session.execute(stmt)
            scrim = result.scalar_one_or_none()

        if not scrim:
            await interaction.response.send_message(
                "This channel is not a valid tournament registration channel.",
                ephemeral=True,
            )
            return

        async with get_db() as session:
            stmt = select(Team).where(Team.secret == code)
            team = (await session.execute(stmt)).scalar_one_or_none()

        if not team:
            await interaction.response.send_message(
                f"No team found with Code `{code}` in this tournament.",
                ephemeral=True,
            )
            return

        async with get_db() as session:
            stmt = select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == interaction.user.id,
            )
            existing_member = (await session.execute(stmt)).scalar_one_or_none()

        if existing_member:
            await interaction.response.send_message(
                f"You are already a member of the team `{team.name}`.",
                ephemeral=True,
            )
            return

        async with get_db() as session:
            stmt = select(count(TeamMember.id)).where(
                TeamMember.team_id == team.id,
            )
            result = await session.execute(stmt)
            member_count = result.scalar_one_or_none() or 0

        if member_count >= team.max_size:
            await interaction.response.send_message(
                f"The team `{team.name}` is already full. "
                f"It can have a maximum of {team.max_size} members.",
                ephemeral=True,
            )
            return

        async with get_db() as session:
            team_member = TeamMember(
                team_id=team.id,
                user_id=interaction.user.id,
                scrim_id=scrim.id,
            )
            session.add(team_member)
            await session.commit()

        await interaction.response.send_message(
            f"You have successfully joined the team `{team.name}`!",
            ephemeral=True,
        )

    async def cog_load(self):
        print("Tournament cog loaded.")
        await super().cog_load()

    async def cog_unload(self):
        print("Tournament cog unloaded.")
        await super().cog_unload()


async def setup(bot: Bot):
    await bot.add_cog(Tournament(bot))
