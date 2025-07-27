from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Self
import discord

if TYPE_CHECKING:
    from extended_types import GuildInteraction

class SetupStep2(discord.ui.Modal, title="Scrim Setup - Step 2"):
    date = discord.ui.TextInput[Self](
        label="Scrim Date",
        placeholder="Enter the date of the scrim (YYYY-MM-DD)",
        required=True,
        max_length=10,
    )
    time = discord.ui.TextInput[Self](
        label="Scrim Time",
        placeholder="Enter the time of the scrim (HH:MM)",
        required=True,
        max_length=5,
    )

    async def on_submit(self, interaction: GuildInteraction) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        from modals.setup.step2_button import Step2Button

        try:
            date = datetime.strptime(self.date.value, "%Y-%m-%d").date()
        except ValueError:
            embed = discord.Embed(
                title="Invalid Date Format",
                description=(
                    f"❌ You entered: `{self.date.value}`\n\n"
                    "Please enter the date in **YYYY-MM-DD** format.\n"
                    "Example: `2025-07-30`"
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True, view=Step2Button("Try Again")
            )
            return

        try:
            time = datetime.strptime(self.time.value, "%H:%M").time()
        except ValueError:
            embed = discord.Embed(
                title="Invalid Time Format",
                description=(
                    f"❌ You entered: `{self.time.value}`\n\n"
                    "Please enter the time in **HH:MM** format.\n"
                    "Example: `14:30`"
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True, view=Step2Button("Try Again")
            )
            return

        scrim_datetime = datetime.combine(date, time)
        embed = discord.Embed(
            title="✅ Scrim Scheduled",
            description=f"Your scrim has been scheduled for **{scrim_datetime.strftime('%Y-%m-%d %H:%M')} UTC**.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

