from typing import Self
import discord

from ui.view.user_only_view import UserOnlyView


class Confirm(UserOnlyView):
    def __init__(self, user_id: int):
        super().__init__(user_id=user_id)
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        self.value = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        self.value = False
        await interaction.response.defer()
        self.stop()
