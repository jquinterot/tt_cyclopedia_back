"""add is_admin column to users

Revision ID: add_is_admin_column
Revises: 5face0d7b746
Create Date: 2025-03-16 10:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_is_admin_column'
down_revision: str | None = '5face0d7b746'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add is_admin column to users table."""
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    """Remove is_admin column from users table."""
    op.drop_column('users', 'is_admin')
