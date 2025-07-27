from discord import Embed
from data.scrim_config import ScrimConfig
from config import settings


class ScrimConfigEmbed(Embed):
    def __init__(self, scrim_config: ScrimConfig):
        super().__init__(
            title="🟦 Scrim Configuration", color=settings.default_brand_color
        )

        description = "━━━━━━━━━━━━━━━━━━━━━━━"

        def with_prefix(role: str) -> str:
            return (
                f"@{role} - {scrim_config.scrim_name}"
                if scrim_config.prefix_roles
                else f"@{role}"
            )

        lines = [
            f"• **Organizer Role:**         {with_prefix(scrim_config.organizer_role_name)}",
            f"• **Participant Role:**       {with_prefix(scrim_config.participant_role_name)}",
            f"• **Prefix Roles Enabled:**   {'Yes' if scrim_config.prefix_roles else 'No'}",
            "",
            f"• **Scrim Name:**             {scrim_config.scrim_name or 'Not set'}",
            f"• **Date:**                   {scrim_config.date_input or 'Not set'}",
            f"• **Time:**                   {scrim_config.time_input or 'Not set'}",
            "━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        description += "\n" + "\n".join(lines)
        self.description = description
