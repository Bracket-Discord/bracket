from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from typing import Self

from data.scrim_config import ScrimConfig
from ui.setup.embeds.scrim_config_embed import ScrimConfigEmbed

if TYPE_CHECKING:
    from extended_types import GuildInteraction


class BasicConfigFinalize(discord.ui.View):
    def __init__(
        self,
        scrim_config: ScrimConfig,
    ) -> None:
        super().__init__(timeout=None)
        self.scrim_config = scrim_config

    @discord.ui.select(
        placeholder="Prefix roles with scrim name?",
        options=[
            discord.SelectOption(
                label="Yes",
                value="yes",
                description="Prefix roles with the scrim name.",
                default=True,
            ),
            discord.SelectOption(
                label="No",
                value="no",
                description="Do not prefix roles with the scrim name.",
            ),
        ],
    )
    async def step1_select_callback(
        self, interaction: GuildInteraction, select: discord.ui.Select[Self]
    ):
        value = select.values[0]
        if value == "yes":
            self.scrim_config.prefix_roles = True
        else:
            self.scrim_config.prefix_roles = False

        for option in select.options:
            option.default = False
            if option.value == value:
                option.default = True

        await interaction.response.edit_message(
            embed=ScrimConfigEmbed(self.scrim_config),
            view=self,
        )

    @discord.ui.button(
        label="Proceed to Timing Configuration", style=discord.ButtonStyle.primary
    )
    async def step2_button_callback(
        self, interaction: GuildInteraction, button: discord.ui.Button[Self]
    ):
        from ui.setup.timing.timing_config_modal import TimingConfigModal

        await interaction.response.send_modal(TimingConfigModal(self.scrim_config))
