"""add_column_enable_to_users_table

Revision ID: 9239ff1f9e63
Revises: b2cbf427a97b
Create Date: 2025-12-14 18:52:17.319644

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9239ff1f9e63"
down_revision: Union[str, None] = "b2cbf427a97b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("enable", sa.Boolean, nullable=True, default=False)
    )
    op.execute("""
        UPDATE users SET enable=FALSE, updated_at = NOW();
    """)
    op.alter_column("users", "enable", nullable=False, type_=sa.Boolean)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "enable")
