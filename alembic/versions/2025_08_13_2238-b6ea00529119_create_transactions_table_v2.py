"""create_transactions_table_v2

Revision ID: b6ea00529119
Revises: d19b4a200b17
Create Date: 2025-08-13 22:38:58.718493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b6ea00529119'
down_revision: Union[str, None] = 'd19b4a200b17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

transaction_type = sa.Enum('INCOME', 'EXPENSE', 'TRANSFER', name='transaction_type')


def upgrade() -> None:
    """Upgrade schema."""
    transaction_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'transactions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('amount_cents', sa.Numeric(15, 2), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('category_id', sa.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('macro_category_id', sa.UUID(as_uuid=True), sa.ForeignKey('macro_categories.id'), nullable=True),
        sa.Column('type', transaction_type, nullable=False),
        sa.Column('management_period_id', sa.UUID(as_uuid=True), sa.ForeignKey('management_period.id'), nullable=False),
        sa.Column('source_account_id', sa.UUID(as_uuid=True), sa.ForeignKey('accounts.id'), nullable=True),
        sa.Column('destination_account_id', sa.UUID(as_uuid=True), sa.ForeignKey('accounts.id'), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('currency', sa.String(length=5), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('transactions')
    transaction_type.drop(op.get_bind(), checkfirst=True)
