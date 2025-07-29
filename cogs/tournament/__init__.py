from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Self
from discord import app_commands
import discord
from discord.ext import commands

from cogs.tournament.config import BestOf, BracketType, ScrimConfig, TournamentType
from cogs.tournament.embeds import ScrimConfigEmbed

if TYPE_CHECKING:
    from bot import Bot
    from extended_types import GuildInteraction


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
            embed=ScrimConfigEmbed(self.scrim_config), view=None
        )


class Tournament(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.guild_only()
    async def setup(self, interaction: GuildInteraction):
        scrim_config = ScrimConfig()
        modal = BasicConfigModal(scrim_config=scrim_config)
        await interaction.response.send_modal(modal)


async def setup(bot: Bot):
    await bot.add_cog(Tournament(bot))
