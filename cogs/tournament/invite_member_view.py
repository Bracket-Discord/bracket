from __future__ import annotations
import discord
from discord.ui import UserSelect
from typing import Self


class InviteMemberView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 60.0):
        super().__init__(timeout=timeout)
        self.users: list[discord.User | discord.Member] = []

    @discord.ui.select(
        cls=UserSelect,
        min_values=1,
        max_values=5,
        placeholder="Select members to invite",
    )
    async def select_callback(
        self, interaction: discord.Interaction, select: UserSelect[Self]
    ):
        await interaction.response.defer()
        self.users = select.values
        self.stop()
