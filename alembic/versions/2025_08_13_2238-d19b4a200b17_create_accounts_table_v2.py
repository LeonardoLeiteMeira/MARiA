"""create_accounts_table_v2

Revision ID: d19b4a200b17
Revises: 5241c0f65ee9
Create Date: 2025-08-13 22:38:50.418568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd19b4a200b17'
down_revision: Union[str, None] = '5241c0f65ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_account_type = sa.Enum(
    'CREDIT_CARD', 'CHECKING', 'SAVINGS', 'WALLET', name='user_account_type', create_type=False,  
)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'accounts',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('type', user_account_type, nullable=False),
        sa.Column('opening_balance_cents', sa.Numeric(15, 2), server_default='0', nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('currency', sa.String(length=5), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('accounts')
