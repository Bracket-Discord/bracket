from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScrimConfig:
    organizer_role_name: str = field(default="Organizer")
    participant_role_name: str = field(default="Participant")
    prefix_roles: bool = field(default=False)
    max_participants: int = field(default=10)
    scrim_name: Optional[str] = field(default=None)
    date_input: Optional[str] = field(default=None)
    time_input: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    rules: Optional[str] = field(default=None)
    best_of: Optional[int] = field(default=None)
