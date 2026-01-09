import uuid
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy import String, ForeignKey

from database.configs.base import BaseModel


class PluggyLoanModel(BaseModel):
    __tablename__ = "pluggy_loans"

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
    contract_number: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    product_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    contract_amount: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False,
    )
    currency_code: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    complementary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<PluggyLoanModel(id={self.id}, user_id={self.user_id}, contract_number={self.contract_number})>"
