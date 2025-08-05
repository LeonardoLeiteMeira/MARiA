"""create_table_pluggy_item

Revision ID: cf57fd586e8d
Revises: e879fb9293c8
Create Date: 2025-08-03 18:40:38.638994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'cf57fd586e8d'
down_revision: Union[str, None] = 'e879fb9293c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pluggy_items",
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('item_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('connector', postgresql.JSONB, nullable=False),
        sa.Column('products', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('execution_status', sa.String(), nullable=False),
        sa.Column('complementary_data', postgresql.JSONB, nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('connected_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("pluggy_items")
