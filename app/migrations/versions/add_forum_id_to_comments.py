"""add_forum_id_to_comments

Revision ID: add_forum_id_to_comments
Revises: 17c5bb3d8f46
Create Date: 2025-06-27 23:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_forum_id_to_comments'
down_revision: Union[str, None] = '17c5bb3d8f46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add forum_id column to comments table."""
    op.add_column('comments', sa.Column('forum_id', sa.String(length=255), nullable=True), schema='cyclopedia_owner')
    op.create_foreign_key('fk_comments_forum_id', 'comments', 'forums', ['forum_id'], ['id'], ondelete='CASCADE', source_schema='cyclopedia_owner', referent_schema='cyclopedia_owner')


def downgrade() -> None:
    """Remove forum_id column from comments table."""
    op.drop_constraint('fk_comments_forum_id', 'comments', type_='foreignkey', schema='cyclopedia_owner')
    op.drop_column('comments', 'forum_id', schema='cyclopedia_owner') 