"""add equipment_id to posts

Revision ID: add_equipment_id_to_posts
Revises: add_equipment_tables
Create Date: 2026-05-06 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_equipment_id_to_posts'
down_revision: Union[str, None] = 'add_equipment_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add equipment_id column to posts table."""
    op.add_column('posts', sa.Column('equipment_id', sa.String(255), nullable=True))
    op.create_foreign_key(
        'fk_posts_equipment',
        'posts', 'equipment',
        ['equipment_id'], ['id']
    )


def downgrade() -> None:
    """Remove equipment_id column from posts table."""
    op.drop_constraint('fk_posts_equipment', 'posts', type_='foreignkey')
    op.drop_column('posts', 'equipment_id')
