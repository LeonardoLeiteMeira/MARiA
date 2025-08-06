"""create_investments_and_loans_table

Revision ID: 1b2b3c4d5e67
Revises: d9d012dfa75f
Create Date: 2025-08-05 16:05:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1b2b3c4d5e67'
down_revision: Union[str, None] = 'd9d012dfa75f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'pluggy_investments',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('subtype', sa.String(), nullable=True),
        sa.Column('balance', sa.NUMERIC, nullable=True),
        sa.Column('complementary_data', postgresql.JSONB, nullable=False),
    )

    op.create_table(
        'pluggy_investment_transactions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('investment_id', sa.UUID(as_uuid=True), sa.ForeignKey('pluggy_investments.id'), nullable=False),
        sa.Column('amount', sa.NUMERIC, nullable=False),
        sa.Column('value', sa.NUMERIC, nullable=False),
        sa.Column('quantity', sa.NUMERIC, nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('movement_type', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('complementary_data', postgresql.JSONB, nullable=False),
    )

    op.create_table(
        'pluggy_loans',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('contract_number', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('contract_amount', sa.NUMERIC, nullable=False),
        sa.Column('currency_code', sa.String(), nullable=True),
        sa.Column('complementary_data', postgresql.JSONB, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pluggy_loans')
    op.drop_table('pluggy_investment_transactions')
    op.drop_table('pluggy_investments')
