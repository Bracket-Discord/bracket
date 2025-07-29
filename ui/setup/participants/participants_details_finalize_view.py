from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from typing import Self

from data.scrim_config import ScrimConfig

if TYPE_CHECKING:
    from extended_types import GuildInteraction


class ParticipantDetailsFinalize(discord.ui.View):
    def __init__(
        self,
        scrim_config: ScrimConfig,
    ) -> None:
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    @discord.ui.button(
        label="Proceed to Timing Configuration", style=discord.ButtonStyle.primary
    )
    async def step2_button_callback(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        from ui.setup.timing.timing_config_modal import TimingConfigModal

        await interaction.response.send_modal(TimingConfigModal(self.scrim_config))
