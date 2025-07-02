"""create cyclopedia_owner schema

Revision ID: 0001_create_schema
Revises: 
Create Date: 2025-07-01 00:00:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0001_create_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS cyclopedia_owner")

def downgrade():
    op.execute("DROP SCHEMA IF EXISTS cyclopedia_owner CASCADE") 