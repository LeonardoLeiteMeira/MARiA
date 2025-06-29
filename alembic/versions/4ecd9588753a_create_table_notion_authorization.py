"""create_table_notion_authorization

Revision ID: 4ecd9588753a
Revises: 24a803bbcf33
Create Date: 2025-06-15 17:30:25.501396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4ecd9588753a'
down_revision: Union[str, None] = '24a803bbcf33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notion_authorizations",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bot_id", sa.String(length=255), nullable=False),
        sa.Column("access_token", sa.String(length=512), nullable=False),
        sa.Column("workspace_id", sa.String(length=255), nullable=False),
        sa.Column("workspace_name", sa.String(length=255), nullable=False),
        sa.Column("workspace_icon", sa.String(length=255), nullable=True),
        sa.Column("owner_type", sa.Enum('workspace','user', name='ownertype'), nullable=False),
        sa.Column("owner_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("bot_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("notion_authorizations")
    op.execute("DROP TYPE IF EXISTS ownertype")
