"""create_accounts_table

Revision ID: 1084407825df
Revises: cf57fd586e8d
Create Date: 2025-08-04 14:12:14.004394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1084407825df'
down_revision: Union[str, None] = 'cf57fd586e8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "pluggy_accounts",
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('marketing_name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('complementary_data', postgresql.JSONB, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pluggy_accounts')
