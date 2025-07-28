from data.scrim_config import ScrimConfig
from db.models.scrim import Scrim

from db.models.base import SessionLocal
from datetime import datetime


def save_scrim_config(scrim_config: ScrimConfig) -> Scrim:
    db = SessionLocal()
    try:
        # Combine date and time into datetime
        scrim_datetime = None
        if scrim_config.date_input and scrim_config.time_input:
            try:
                combined_str = f"{scrim_config.date_input} {scrim_config.time_input}"
                scrim_datetime = datetime.strptime(combined_str, "%Y-%m-%d %H:%M")
            except ValueError:
                scrim_datetime = None  # log if needed

        scrim = Scrim(
            name=scrim_config.scrim_name or "New Scrim",
            guild_id=0,
            category_id=None,
            admin_channel_id=None,
            participant_role_id=None,
            organizer_role_id=None,
            scrim_time=scrim_datetime,
        )

        scrim.config = ScrimConfig(
            organizer_role_name=scrim_config.organizer_role_name,
            participant_role_name=scrim_config.participant_role_name,
            prefix_roles=scrim_config.prefix_roles,
            max_participants=scrim_config.max_participants,
            scrim_name=scrim_config.scrim_name,
            date_input=scrim_config.date_input,
            time_input=scrim_config.time_input,
            description=scrim_config.description,
            rules=scrim_config.rules,
            best_of=scrim_config.best_of,
        )

        db.add(scrim)
        db.commit()
        db.refresh(scrim)
        return scrim
    finally:
        db.close()
