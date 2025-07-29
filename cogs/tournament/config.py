from dataclasses import dataclass, field

from enum import Enum
from typing import Optional


class BracketType(Enum):
    SINGLE_ELIMINATION = 1
    DOUBLE_ELIMINATION = 2
    ROUND_ROBIN = 3
    SWISS = 4


class BestOf(Enum):
    BO1 = 1
    BO3 = 3
    BO5 = 5


class TournamentType(Enum):
    SOLO = 1
    DUO = 2
    TEAM = 3


@dataclass
class ScrimConfig:
    organizer_role_name: str = field(default="Organizer")
    participant_role_name: str = field(default="Participant")
    prefix_roles: bool = field(default=False)
    teamcap: int = field(default=5)
    scrim_name: Optional[str] = field(default=None)
    date_input: Optional[str] = field(default=None)
    time_input: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    rules: Optional[str] = field(default=None)
    tournament_type: Optional[TournamentType] = field(default=None)
    bracket_type: Optional[BracketType] = field(default=None)
    best_of: Optional[BestOf] = field(default=None)
    prize: Optional[str] = field(default=None)
