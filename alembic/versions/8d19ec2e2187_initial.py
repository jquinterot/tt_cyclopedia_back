"""initial

Revision ID: 8d19ec2e2187
Revises: 
Create Date: 2025-04-27 15:04:58.688611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d19ec2e2187'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('id', sa.String(length=255), nullable=False),
                    sa.Column('username', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='cyclopedia_owner',
                    if_not_exists=True
                    )

    op.create_table('posts',
                    sa.Column('id', sa.String(length=255), nullable=False),
                    sa.Column('title', sa.String(length=255), nullable=False),
                    sa.Column('content', sa.Text(), nullable=False),
                    sa.Column('image_url', sa.String(length=512), nullable=False),
                    sa.Column('likes', sa.Integer(), server_default='0'),
                    sa.PrimaryKeyConstraint('id'),
                    schema='cyclopedia_owner',
                    if_not_exists=True

                    )

    op.create_table('comments',
                    sa.Column('id', sa.String(length=255), nullable=False),
                    sa.Column('comment', sa.String(length=255), nullable=False),
                    sa.Column('post_id', sa.String(length=255), nullable=False),
                    sa.Column('user_id', sa.String(length=255), nullable=False),
                    sa.ForeignKeyConstraint(['post_id'], ['cyclopedia_owner.posts.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['cyclopedia_owner.users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    schema='cyclopedia_owner',
                    if_not_exists=True
                    )
    # ### end Alembic commands ###

def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments', schema='cyclopedia_owner')
    op.drop_table('posts', schema='cyclopedia_owner')
    op.drop_table('users', schema='cyclopedia_owner')
    # ### end Alembic commands ###