from __future__ import annotations
import discord
from typing import TYPE_CHECKING, Self

from db import get_db
from db.models.scrim import Scrim
from modals.setup.step2_button import Step2Button

if TYPE_CHECKING:
    from extended_types import GuildInteraction


class SetupStep1(discord.ui.Modal, title="Scrim Setup - Step 1"):
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

    async def create_role_safe(
        self, guild: discord.Guild, name: str
    ) -> discord.Role | None:
        try:
            return await guild.create_role(name=name, mentionable=True)
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None

    async def on_submit(
        self, interaction: GuildInteraction
    ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        organizer_name = self.organizer_role.value + " - " + self.name.value
        participant_name = self.participant_role.value + " - " + self.name.value

        organizer_role = await self.create_role_safe(interaction.guild, organizer_name)
        if not organizer_role:
            embed = discord.Embed(
                title="❌ Failed to Create Organizer Role",
                description=f"Could not create role `{organizer_name}`. Make sure the bot has `Manage Roles` permission and the role name is valid.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True, view=Step2Button("Try Again")
            )
            return

        participant_role = await self.create_role_safe(
            interaction.guild, participant_name
        )
        if not participant_role:
            embed = discord.Embed(
                title="❌ Failed to Create Participant Role",
                description=f"Could not create role `{participant_name}`. Make sure the bot has `Manage Roles` permission and the role name is valid.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=embed, ephemeral=True, view=Step2Button("Try Again")
            )
            return

        async with get_db() as session:
            scrim = Scrim(
                name=self.name.value,
                guild_id=interaction.guild_id,
                organizer_role_id=organizer_role.id,
                participant_role_id=participant_role.id,
            )
            session.add(scrim)
            await session.commit()

        embed = discord.Embed(
            title="✅ Scrim Setup Complete",
            description=(
                f"Scrim **{self.name.value}** has been set up successfully!\n\n"
                f"**Organizer Role:** {organizer_role.mention}\n"
                f"**Participant Role:** {participant_role.mention}"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(
            embed=embed, ephemeral=True, view=Step2Button()
        )
