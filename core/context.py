from __future__ import annotations
from discord import Guild, Member
from discord.ext import commands
from core.bracket import BracketBot


Context = commands.Context[BracketBot]


class GuildContext(commands.Context[BracketBot]):
    """Context for guild-specific commands."""

    guild: Guild  # pyright: ignore[reportIncompatibleVariableOverride]
    author: Member  # pyright: ignore[reportIncompatibleVariableOverride]
