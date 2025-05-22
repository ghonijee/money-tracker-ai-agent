"""create table transaction

Revision ID: df05050b4bda
Revises:
Create Date: 2025-05-11 01:41:32.129409

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "df05050b4bda"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.create_table(
		"transaction",
		sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
		sa.Column("user_id", sa.String(length=255), nullable=False),
		sa.Column("date", sa.DateTime(), nullable=False),
		sa.Column("amount", sa.Float(), nullable=False),
		sa.Column("description", sa.String(length=255), nullable=True),
		sa.Column("category", sa.String(length=100), nullable=True),
		sa.Column("type", sa.Enum("expense", "income", name="type"), nullable=True),
		sa.PrimaryKeyConstraint("id"),
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_table("transaction")
