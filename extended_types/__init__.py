from __future__ import annotations
from typing import TYPE_CHECKING
from discord import Interaction
from discord.guild import Guild

if TYPE_CHECKING:
    from bot import Bot


class GuildInteraction(Interaction[Bot]):
    guild: Guild  # pyright: ignore
