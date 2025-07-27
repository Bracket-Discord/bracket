from __future__ import annotations
import discord
from typing import TYPE_CHECKING, Self

from data.scrim_config import ScrimConfig
from modals.setup.basic.basic_config_finalize_view import BasicConfigFinalize
from modals.setup.embeds.scrim_config_embed import ScrimConfigEmbed

if TYPE_CHECKING:
    from extended_types import GuildInteraction


class BasicConfigModal(discord.ui.Modal, title="Scrim Setup - Step 1"):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(timeout=None)
        self.scrim_config = scrim_config
        self.name.default = scrim_config.scrim_name
        self.organizer_role.default = scrim_config.organizer_role_name
        self.participant_role.default = scrim_config.participant_role_name

    name = discord.ui.TextInput[Self](
        label="Scrim Name",
        placeholder="Enter the name of the scrim",
        required=True,
        max_length=100,
    )
    organizer_role = discord.ui.TextInput[Self](
        label="Organizer Role",
        placeholder="Enter the name of the organizer role",
        max_length=50,
        default="Organizer",
    )
    participant_role = discord.ui.TextInput[Self](
        label="Participant Role",
        placeholder="Enter the name of the participant role",
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
            view=BasicConfigFinalize(scrim_config),
            ephemeral=True,
        )
