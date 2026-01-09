"""set_pluggy_collumns_as_nullable

Revision ID: f8c70eedb0b3
Revises: 1b2b3c4d5e67
Create Date: 2025-08-07 17:49:19.578021

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f8c70eedb0b3"
down_revision: Union[str, None] = "1b2b3c4d5e67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "pluggy_items", "connector", existing_type=postgresql.JSONB, nullable=True
    )
    op.alter_column(
        "pluggy_items", "products", existing_type=sa.ARRAY(sa.String()), nullable=True
    )
    op.alter_column(
        "pluggy_items", "execution_status", existing_type=sa.String(), nullable=True
    )
    op.alter_column("pluggy_items", "status", existing_type=sa.String(), nullable=True)
    op.alter_column(
        "pluggy_items", "last_updated_at", existing_type=sa.DateTime(), nullable=True
    )
    op.alter_column(
        "pluggy_items", "created_at", existing_type=sa.DateTime(), nullable=True
    )
    op.alter_column(
        "pluggy_items", "connected_at", existing_type=sa.DateTime(), nullable=True
    )
    op.alter_column(
        "pluggy_investments", "code", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "pluggy_investments", "name", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "pluggy_investments", "type", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "pluggy_investments", "subtype", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "pluggy_investments", "balance", existing_type=sa.NUMERIC, nullable=True
    )

    op.alter_column(
        "pluggy_investment_transactions",
        "amount",
        existing_type=sa.NUMERIC,
        nullable=True,
    )
    op.alter_column(
        "pluggy_investment_transactions",
        "value",
        existing_type=sa.NUMERIC,
        nullable=True,
    )
    op.alter_column(
        "pluggy_investment_transactions",
        "quantity",
        existing_type=sa.NUMERIC,
        nullable=True,
    )
    op.alter_column(
        "pluggy_investment_transactions",
        "type",
        existing_type=sa.String(),
        nullable=True,
    )
    op.alter_column(
        "pluggy_investment_transactions",
        "movement_type",
        existing_type=sa.String(),
        nullable=True,
    )

    # Set pluggy_loans columns as nullable
    op.alter_column(
        "pluggy_loans", "contract_number", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "pluggy_loans", "product_name", existing_type=sa.String(), nullable=True
    )
    op.alter_column("pluggy_loans", "type", existing_type=sa.String(), nullable=True)
    op.alter_column(
        "pluggy_loans", "contract_amount", existing_type=sa.NUMERIC, nullable=True
    )
    op.alter_column(
        "pluggy_loans", "currency_code", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "pluggy_card_bills", "total_amount", existing_type=sa.NUMERIC, nullable=True
    )
    op.alter_column(
        "pluggy_transactions", "amount", existing_type=sa.NUMERIC, nullable=True
    )
    op.alter_column(
        "pluggy_transactions", "status", existing_type=sa.String(), nullable=True
    )

    op.alter_column(
        "pluggy_transactions", "type", existing_type=sa.String(), nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
