"""create_bills_table

Revision ID: d9d012dfa75f
Revises: 9510e51552a6
Create Date: 2025-08-05 09:02:36.600471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd9d012dfa75f'
down_revision: Union[str, None] = '9510e51552a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pluggy_card_bills",
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('account_id', sa.UUID(as_uuid=True), sa.ForeignKey('pluggy_accounts.id'), nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('total_amount', sa.NUMERIC, nullable=False),
        sa.Column('minimum_payment_amount', sa.NUMERIC, nullable=False),
        sa.Column('complementary_data', postgresql.JSONB, nullable=False),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pluggy_card_bills')
