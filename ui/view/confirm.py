from typing import Self
import discord


class Confirm(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.value = None
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot interact with this confirmation.", ephemeral=True
            )
            return False
        return True

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
