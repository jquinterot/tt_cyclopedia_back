"""merge schema and forum_id branches

Revision ID: e25d20f5644c
Revises: 0001_create_schema, add_forum_id_to_comments
Create Date: 2025-07-01 22:14:49.515554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e25d20f5644c'
down_revision: Union[str, None] = 'add_forum_id_to_comments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
