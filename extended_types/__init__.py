from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Interaction
from discord.guild import Guild

if TYPE_CHECKING:
    from core.bracket import BracketBot


class GuildInteraction(Interaction[BracketBot]):
    guild: Guild  # pyright: ignore
