from typing import Optional
from discord import Embed

from cogs.tournament.config import BestOf, BracketType, ScrimConfig, TournamentType
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
            f"• **Scrim Name:**             {scrim_config.scrim_name or 'Not set'}",
            f"• **Organizer Role:**         {with_prefix(scrim_config.organizer_role_name)}",
            f"• **Participant Role:**       {with_prefix(scrim_config.participant_role_name)}",
            f"• **Prefix Roles Enabled:**   {'Yes' if scrim_config.prefix_roles else 'No'}",
            "",
            f"• **Rules:**                  {'\N{WHITE HEAVY CHECK MARK}' if scrim_config.rules else 'No rules specified'}",
            f"• **Description:**            {'\N{WHITE HEAVY CHECK MARK}' if scrim_config.description else 'Not provided'}",
            f"• **Max Participants:**       {scrim_config.max_participants}",
            "",
            f"• **Best of:**                {format_best_of(scrim_config.best_of)}",
            f"• **Bracket Type:**           {format_bracket_type(scrim_config.bracket_type)}",
            f"• **Tournament Type:**        {format_tournament_type(scrim_config.tournament_type)}",
            "",
            f"• **Date:**                   {scrim_config.date_input or 'Not set'}",
            f"• **Time:**                   {scrim_config.time_input or 'Not set'}",
            "━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        description += "\n" + "\n".join(lines)
        self.description = description


def format_bracket_type(bracket_type: Optional[BracketType]) -> str:
    if not bracket_type:
        return "Not set"
    match bracket_type:
        case BracketType.SINGLE_ELIMINATION:
            return "Single Elimination"
        case BracketType.DOUBLE_ELIMINATION:
            return "Double Elimination"
        case BracketType.ROUND_ROBIN:
            return "Round Robin"
        case BracketType.SWISS:
            return "Swiss"


def format_tournament_type(tournament_type: Optional[TournamentType]) -> str:
    if not tournament_type:
        return "Not set"
    match tournament_type:
        case TournamentType.SOLO:
            return "Solo"
        case TournamentType.DUO:
            return "Duo"
        case TournamentType.TEAM:
            return "Team"


def format_best_of(best_of: Optional[BestOf]) -> str:
    if not best_of:
        return "Not set"
    match best_of:
        case BestOf.BO1:
            return "Best of 1 (BO1)"
        case BestOf.BO3:
            return "Best of 3 (BO3)"
        case BestOf.BO5:
            return "Best of 5 (BO5)"
