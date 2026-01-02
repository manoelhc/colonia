"""add context_stacks and context_environments tables

Revision ID: a1b2c3d4e5f6
Revises: f8c3d4e2a1b9
Create Date: 2026-01-02 18:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f8c3d4e2a1b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create context_stacks table
    op.create_table('context_stacks',
    sa.Column('context_id', sa.Integer(), nullable=False),
    sa.Column('stack_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['context_id'], ['contexts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stack_id'], ['stacks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('context_id', 'stack_id')
    )
    
    # Create context_environments table
    op.create_table('context_environments',
    sa.Column('context_id', sa.Integer(), nullable=False),
    sa.Column('environment_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['context_id'], ['contexts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['environment_id'], ['environments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('context_id', 'environment_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('context_environments')
    op.drop_table('context_stacks')
