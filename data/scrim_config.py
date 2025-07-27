from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScrimConfig:
    organizer_role_name: str = field(default="Organizer")
    participant_role_name: str = field(default="Participant")
    prefix_roles: bool = field(default=True)
    scrim_name: Optional[str] = field(default=None)
    date_input: Optional[str] = field(default=None)
    time_input: Optional[str] = field(default=None)
