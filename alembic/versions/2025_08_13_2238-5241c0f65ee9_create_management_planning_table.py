"""create_management_planning_table

Revision ID: 5241c0f65ee9
Revises: b5c4fc971887
Create Date: 2025-08-13 22:38:41.640147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '5241c0f65ee9'
down_revision: Union[str, None] = 'b5c4fc971887'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'management_planning',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('category_id', sa.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('planned_value_cents', sa.Numeric(15, 2), server_default='0', nullable=False),
        sa.Column('management_period_id', sa.UUID(as_uuid=True), sa.ForeignKey('management_period.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('management_planning')
