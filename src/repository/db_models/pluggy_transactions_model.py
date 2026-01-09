import uuid
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy import String, ForeignKey

from database.configs.base import BaseModel

class PluggyTransactionModel(BaseModel):
    __tablename__ = "pluggy_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('pluggy_accounts.id'),
        nullable=False
    )
    amount: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False
    )
    balance: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    complementary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<PluggyTransactionModel(id={self.id}, user_id={self.user_id}, "
            f"account_id={self.account_id}, amount={self.amount})>"
        )
