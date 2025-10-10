"""create_soft_delete_for_accounts

Revision ID: b2cbf427a97b
Revises: 90f0b1625fc3
Create Date: 2025-10-10 19:26:01.434180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2cbf427a97b'
down_revision: Union[str, None] = '90f0b1625fc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("accounts", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("accounts", "deleted_at")
