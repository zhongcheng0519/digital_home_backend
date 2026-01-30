"""add category to todo table

Revision ID: 003_add_category
Revises: 002_add_todo
Create Date: 2026-01-02 15:45:30.409021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

revision: str = '003_add_category'
down_revision: Union[str, None] = '002_add_todo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('family_member', 'role',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('milestone', 'content_ciphertext',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('milestone', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.add_column('todo', sa.Column('category', sa.String(), nullable=True))
    op.alter_column('todo', 'title_ciphertext',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('todo', 'is_completed',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('todo', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('todo', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)


def downgrade() -> None:
    op.alter_column('todo', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('todo', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('todo', 'is_completed',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('todo', 'title_ciphertext',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('todo', 'category')
    op.alter_column('milestone', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('milestone', 'content_ciphertext',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('family_member', 'role',
               existing_type=sa.VARCHAR(),
               nullable=True)
