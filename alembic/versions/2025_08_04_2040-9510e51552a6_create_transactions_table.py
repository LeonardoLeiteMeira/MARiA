"""create_transactions_table

Revision ID: 9510e51552a6
Revises: 1084407825df
Create Date: 2025-08-04 20:40:46.074823

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9510e51552a6"
down_revision: Union[str, None] = "1084407825df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pluggy_transactions",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "account_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("pluggy_accounts.id"),
            nullable=False,
        ),
        sa.Column("amount", sa.NUMERIC, nullable=False),
        sa.Column("balance", sa.NUMERIC, nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("complementary_data", postgresql.JSONB, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("pluggy_transactions")
