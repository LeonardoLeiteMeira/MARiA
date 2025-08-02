"""add_password_to_users

Revision ID: 6e28d35dcb27
Revises: 47220b215028
Create Date: 2025-08-02 15:19:30.415370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e28d35dcb27'
down_revision: Union[str, None] = '47220b215028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("password", sa.String(length=255), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password")
