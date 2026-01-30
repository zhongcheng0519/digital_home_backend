"""add todo table

Revision ID: 002_add_todo
Revises: 001_initial
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '002_add_todo'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'todo',
        sa.Column('id', sa.Integer(), nullable=True),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('title_ciphertext', sa.String(), nullable=False),
        sa.Column('description_ciphertext', sa.String(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_todo_family_id'), 'todo', ['family_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_todo_family_id'), table_name='todo')
    op.drop_table('todo')
