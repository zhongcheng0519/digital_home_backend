"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=True),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('public_key', sa.String(), nullable=True),
        sa.Column('encrypted_private_key', sa.String(), nullable=True),
        sa.Column('private_key_salt', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_phone'), 'user', ['phone'], unique=True)
    
    op.create_table(
        'family',
        sa.Column('id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'family_member',
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('encrypted_family_key', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('family_id', 'user_id')
    )
    
    op.create_table(
        'milestone',
        sa.Column('id', sa.Integer(), nullable=True),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('content_ciphertext', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['family_id'], ['family.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_milestone_family_id'), 'milestone', ['family_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_milestone_family_id'), table_name='milestone')
    op.drop_table('milestone')
    op.drop_table('family_member')
    op.drop_table('family')
    op.drop_index(op.f('ix_user_phone'), table_name='user')
    op.drop_table('user')
