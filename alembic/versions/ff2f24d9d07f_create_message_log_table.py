"""Create message_log table

Revision ID: ff2f24d9d07f
Revises: df05050b4bda
Create Date: 2025-05-28 21:06:20.024645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff2f24d9d07f'
down_revision: Union[str, None] = 'df05050b4bda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'message_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('datetime', sa.DateTime, nullable=False),
        sa.Column('message', sa.JSON, nullable=False),
        sa.Column('model', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=True, default=True),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('message_logs')
