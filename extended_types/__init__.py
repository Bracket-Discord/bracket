from discord import Interaction
from discord.guild import Guild


class GuildInteraction(Interaction):
    guild: Guild # pyright: ignore
