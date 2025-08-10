from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.utils import MISSING

if TYPE_CHECKING:
    from core.interaction import Interaction


async def send_message(
    content: str | None = MISSING,
    embed: discord.Embed | None = MISSING,
    ephemeral: bool = False,
    view: discord.ui.View | None = MISSING,
    *,
    interaction: Interaction,
) -> None:
    """
    Sends a message in response to an interaction.
    Args:
        interaction (Interaction): The interaction to respond to.
        content (str | None): The content of the message.
        embed (discord.Embed | None): An optional embed to include in the message.
        ephemeral (bool): Whether the message should be ephemeral (only visible to the user).
    """

    if interaction.response.is_done():
        await interaction.followup.send(
            content=content, embed=embed, ephemeral=ephemeral, view=view
        )
    else:
        await interaction.response.send_message(
            content=content, embed=embed, ephemeral=ephemeral, view=view
        )
