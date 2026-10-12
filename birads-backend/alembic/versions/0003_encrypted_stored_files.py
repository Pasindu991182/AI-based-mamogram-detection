"""encrypted stored files

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-12 18:50:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('stored_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=512), nullable=False),
    sa.Column('content_type', sa.String(length=128), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('stored_files', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_stored_files_path'), ['path'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('stored_files', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_stored_files_path'))

    op.drop_table('stored_files')
