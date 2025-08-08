import discord


class UserOnlyView(discord.ui.View):
    def __init__(self, user_id: int, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        else:
            await interaction.response.send_message(
                "This action is only available to the user who initiated it.",
                ephemeral=True,
            )
            return False
