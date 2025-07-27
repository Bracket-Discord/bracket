from __future__ import annotations
from typing import TYPE_CHECKING, Self
import discord



if TYPE_CHECKING:
    from extended_types import GuildInteraction
    from ui.setup.timing.timing_config_modal import TimingConfigModal


class RetryView(discord.ui.View):
    def __init__(self, previous: TimingConfigModal):
        super().__init__()
        self.previous = previous

    @discord.ui.button(label="Retry", style=discord.ButtonStyle.green)
    async def retry_button(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        await interaction.response.send_modal(self.previous)
