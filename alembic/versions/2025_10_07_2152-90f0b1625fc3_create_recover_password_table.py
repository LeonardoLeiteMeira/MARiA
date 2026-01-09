"""create_recover_password_table

Revision ID: 90f0b1625fc3
Revises: b99a84c24571
Create Date: 2025-10-07 21:52:57.383301

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90f0b1625fc3"
down_revision: Union[str, None] = "b99a84c24571"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "recover_password",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=255), nullable=False),
        sa.Column("limit_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        op.f("ix_recover_password_user_id"),
        "recover_password",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recover_password_code"),
        "recover_password",
        ["code"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_recover_password_code"),
        table_name="recover_password",
    )
    op.drop_index(
        op.f("ix_recover_password_user_id"),
        table_name="recover_password",
    )
    op.drop_table("recover_password")
