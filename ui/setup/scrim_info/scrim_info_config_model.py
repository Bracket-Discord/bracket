from __future__ import annotations
import discord

from data.scrim_config import ScrimConfig
from typing import TYPE_CHECKING, Self

from ui.setup.embeds.scrim_config_embed import ScrimConfigEmbed
from ui.setup.scrim_info.scrim_info_finalize_view import ScrimInfoFinalize


if TYPE_CHECKING:
    from extended_types import GuildInteraction


class ScrimInfoConfigModel(discord.ui.Modal, title="Scrim Info Configuration"):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__()
        self.scrim_config = scrim_config

    def update_scrim_config(self) -> None:
        self.best_of.default = str(self.scrim_config.best_of)
        self.max_participants.default = str(self.scrim_config.max_participants)
        self.rules.default = self.scrim_config.rules or ""
        self.description.default = self.scrim_config.description or ""

    best_of = discord.ui.TextInput[Self](
        label="Best of",
        placeholder="Enter the best of format (e.g., 3, 5, etc.)",
        required=True,
        max_length=2,
    )
    description = discord.ui.TextInput[Self](
        label="Scrim Description",
        placeholder="Enter a brief description of the scrim",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph,
    )
    rules = discord.ui.TextInput[Self](
        label="Scrim Rules",
        placeholder="Enter the rules for the scrim",
        required=False,
        max_length=500,
        style=discord.TextStyle.paragraph,
    )
    max_participants = discord.ui.TextInput[Self](
        label="Max Participants",
        placeholder="Enter the maximum number of participants",
        required=True,
        max_length=3,
        default="10",
    )

    async def on_submit(self, interaction: GuildInteraction) -> None:  # type: ignore
        self_config = self.scrim_config
        self_config.best_of = int(self.best_of.value)
        self_config.description = self.description.value
        self_config.rules = self.rules.value
        self_config.max_participants = int(self.max_participants.value)

        self.update_scrim_config()

        await interaction.response.send_message(
            embed=ScrimConfigEmbed(self.scrim_config),
            ephemeral=True,
            view=ScrimInfoFinalize(scrim_config=self.scrim_config),
        )
