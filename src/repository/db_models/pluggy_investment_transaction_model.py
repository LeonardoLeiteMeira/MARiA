import uuid
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy import String, ForeignKey

from database.configs.base import BaseModel


class PluggyInvestmentTransactionModel(BaseModel):
    __tablename__ = "pluggy_investment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    investment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pluggy_investments.id"),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False,
    )
    value: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    movement_type: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    complementary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PluggyInvestmentTransactionModel(id={self.id}, investment_id={self.investment_id}, amount={self.amount})>"
