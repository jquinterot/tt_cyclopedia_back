"""add equipment tables

Revision ID: add_equipment_tables
Revises: add_is_admin_column
Create Date: 2026-05-06 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_equipment_tables'
down_revision: str | None = 'add_is_admin_column'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create equipment, blade_specs, rubber_specs, and equipment_reviews tables."""
    op.create_table('equipment',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('brand', sa.String(100), nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False, index=True),
        sa.Column('subcategory', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(512), nullable=True),
        sa.Column('price_usd', sa.Float(), nullable=True),
        sa.Column('release_year', sa.Integer(), nullable=True),
        sa.Column('discontinued', sa.Integer(), server_default='0'),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('blade_specs',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('equipment_id', sa.String(255), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('control', sa.Float(), nullable=True),
        sa.Column('stiffness', sa.Float(), nullable=True),
        sa.Column('hardness', sa.Float(), nullable=True),
        sa.Column('weight_min', sa.Integer(), nullable=True),
        sa.Column('weight_max', sa.Integer(), nullable=True),
        sa.Column('plies', sa.Integer(), nullable=True),
        sa.Column('material', sa.String(100), nullable=True),
        sa.Column('thickness', sa.Float(), nullable=True),
        sa.Column('head_size', sa.String(50), nullable=True),
        sa.Column('handle_types', sa.String(200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.UniqueConstraint('equipment_id')
    )

    op.create_table('rubber_specs',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('equipment_id', sa.String(255), nullable=False),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('spin', sa.Float(), nullable=True),
        sa.Column('control', sa.Float(), nullable=True),
        sa.Column('tackiness', sa.Float(), nullable=True),
        sa.Column('grip', sa.Float(), nullable=True),
        sa.Column('sponge_thickness', sa.String(50), nullable=True),
        sa.Column('sponge_hardness', sa.String(50), nullable=True),
        sa.Column('top_sheet', sa.String(100), nullable=True),
        sa.Column('weight', sa.String(50), nullable=True),
        sa.Column('durability', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.UniqueConstraint('equipment_id')
    )

    op.create_table('equipment_reviews',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('equipment_id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('speed_rating', sa.Float(), nullable=True),
        sa.Column('spin_rating', sa.Float(), nullable=True),
        sa.Column('control_rating', sa.Float(), nullable=True),
        sa.Column('review_text', sa.Text(), nullable=True),
        sa.Column('setup_blade_id', sa.String(255), nullable=True),
        sa.Column('setup_rubber_forehand_id', sa.String(255), nullable=True),
        sa.Column('setup_rubber_backhand_id', sa.String(255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.UniqueConstraint('user_id', 'equipment_id', name='_user_equipment_review_uc')
    )


def downgrade() -> None:
    """Drop equipment tables."""
    op.drop_table('equipment_reviews')
    op.drop_table('rubber_specs')
    op.drop_table('blade_specs')
    op.drop_table('equipment')
