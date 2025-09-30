"""add account name

Revision ID: b99a84c24571
Revises: b6ea00529119
Create Date: 2025-09-17 21:36:48.409898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b99a84c24571'
down_revision: Union[str, None] = 'b6ea00529119'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("accounts", sa.Column("name", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("accounts", "name")
