from discord import Embed
import discord

from data.scrim_config import ScrimConfig


class ScrimConfigEmbed(Embed):
    def __init__(self, scrim_config: ScrimConfig):
        def format_role_name(name: str) -> str:
            if not scrim_config.prefix_roles:
                return name
            return f"{name} - {scrim_config.scrim_name}"
        organizer_role_name = format_role_name(scrim_config.organizer_role_name)
        participant_role_name = format_role_name(scrim_config.participant_role_name)
        super().__init__(
            title="Scrim Configuration",
            description=(
                f"**Organizer Role Name:** {organizer_role_name}\n"
                f"**Participant Role Name:** {participant_role_name}\n"
                f"**Prefix Roles:** {'Yes' if scrim_config.prefix_roles else 'No'}\n"
                f"**Scrim Name:** {scrim_config.scrim_name or 'Not set'}\n"
                f"**Date Input:** {scrim_config.date_input or 'Not set'}\n"
                f"**Time Input:** {scrim_config.time_input or 'Not set'}"
            ),
            color=discord.Color.blurple(),
        )
