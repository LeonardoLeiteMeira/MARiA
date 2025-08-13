import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import TIMESTAMP, String, ForeignKey, Numeric, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from database.configs.base import BaseModel


class TransactionType(str, Enum):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    TRANSFER = 'TRANSFER'


class TransactionModel(BaseModel):
    __tablename__ = 'transactions'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now,
        onupdate=datetime.now
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    amount_cents: Mapped[float] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('categories.id'),
        nullable=True
    )
    macro_category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('macro_categories.id'),
        nullable=True
    )
    type: Mapped[TransactionType] = mapped_column(
        SqlEnum(TransactionType, name='transaction_type'),
        nullable=False
    )
    management_period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('management_period.id'),
        nullable=False
    )
    source_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('accounts.id'),
        nullable=True
    )
    destination_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('accounts.id'),
        nullable=True
    )
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(5),
        nullable=False
    )
