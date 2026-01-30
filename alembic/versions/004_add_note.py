"""add note table

Revision ID: 004_add_note
Revises: 003_add_category
Create Date: 2026-01-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004_add_note'
down_revision: Union[str, None] = '003_add_category'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('family_id', sa.Integer(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('title_ciphertext', sa.String(), nullable=True),
    sa.Column('content_ciphertext', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_note_family_id'), 'note', ['family_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_note_family_id'), table_name='note')
    op.drop_table('note')
