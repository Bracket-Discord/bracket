from __future__ import annotations
from typing import TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from core.bracket import BracketBot


Interaction = discord.Interaction[BracketBot]


class GuildInteraction(Interaction):
    guild: discord.Guild  # pyright: ignore[reportIncompatibleMethodOverride]
    user: discord.Member  # pyright: ignore[reportIncompatibleVariableOverride]
