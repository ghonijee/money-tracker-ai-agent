"""create memory_message table

Revision ID: 77b170f6f549
Revises: df05050b4bda
Create Date: 2025-06-10 04:07:15.452911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77b170f6f549'
down_revision: Union[str, None] = 'df05050b4bda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'memory_message',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('memory_message')
