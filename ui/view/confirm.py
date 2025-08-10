from contextlib import suppress
from typing import Self
import discord

from ui.view.user_only_view import UserOnlyView


class Confirm(UserOnlyView):
    def __init__(
        self, user_id: int, clear_on_timeout: bool = True, clear_on_exit: bool = True
    ):
        super().__init__(user_id=user_id)
        self.value = None
        self.clear_on_timeout = clear_on_timeout
        self.clear_on_exit = clear_on_exit
        self.message: discord.Message | None = None
        self.interaction: discord.Interaction | None = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        self.value = True
        await interaction.response.defer()
        self.interaction = interaction
        await self.on_exit()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        self.value = False
        await interaction.response.defer()
        self.interaction = interaction
        await self.on_exit()

    async def on_exit(self) -> None:
        if self.clear_on_exit and self.message is not None:
            with suppress(discord.HTTPException):
                await self.message.edit(view=None)
        self.stop()

    async def on_timeout(self) -> None:
        if self.clear_on_timeout and self.message is not None:
            with suppress(discord.HTTPException):
                await self.message.edit(view=None)
        self.value = None
        self.stop()
