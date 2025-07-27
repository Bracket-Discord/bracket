from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from typing import Self

from modals.setup.step2 import SetupStep2
if TYPE_CHECKING:
    from extended_types import GuildInteraction

class Step2Button(discord.ui.View):
    def __init__(self, label: str = "Continue to Step 2"):
        super().__init__(timeout=None)
        self.step2_button_callback.label = label

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def step2_button_callback(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        await interaction.response.send_modal(SetupStep2())
