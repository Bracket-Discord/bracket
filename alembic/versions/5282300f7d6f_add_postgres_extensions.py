"""add_postgres_extensions

Revision ID: 5282300f7d6f
Revises: 9308e5551939
Create Date: 2025-08-08 14:10:20.870115

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5282300f7d6f"
down_revision: Union[str, Sequence[str], None] = "9308e5551939"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
