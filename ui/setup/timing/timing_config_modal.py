from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Self
import discord

from data.scrim_config import ScrimConfig
from ui.setup.embeds.scrim_config_embed import ScrimConfigEmbed
from ui.setup.timing.retry_view import RetryView

if TYPE_CHECKING:
    from extended_types import GuildInteraction


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
        retry_view = RetryView(self)

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

        await interaction.response.send_message(
            embed=ScrimConfigEmbed(self.scrim_config), ephemeral=True
        )
