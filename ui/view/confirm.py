from typing import Self
import discord


class Confirm(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.value = None
        self.user_id = user_id

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot confirm this action.", ephemeral=True
            )
            return
        # TODO: Implement the confirmation logic here
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You cannot cancel this action.", ephemeral=True
            )
            return

        self.value = False
        self.stop()
