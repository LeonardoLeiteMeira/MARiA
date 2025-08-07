"""set_pluggy_accounts_columns_as_nullable

Revision ID: f33ebbff990b
Revises: f8c70eedb0b3
Create Date: 2025-08-07 18:15:39.673953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f33ebbff990b'
down_revision: Union[str, None] = 'f8c70eedb0b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'pluggy_accounts',
        'name',
        existing_type=sa.String(),
        nullable=True
    )
    op.alter_column(
        'pluggy_accounts',
        'marketing_name',
        existing_type=sa.String(),
        nullable=True
    )
    op.alter_column(
        'pluggy_accounts',
        'type',
        existing_type=sa.String(),
        nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
