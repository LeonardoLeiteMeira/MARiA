import uuid
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, NUMERIC
from sqlalchemy.orm import Mapped, mapped_column

from database.configs.base import BaseModel

class PluggyCardBillModel(BaseModel):
    __tablename__ = "pluggy_card_bills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pluggy_accounts.id"),
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    total_amount: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False
    )
    minimum_payment_amount: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=True
    )
    complementary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )



    def __repr__(self):
        return f"<PluggyCardBillModel(id={self.id}, user_id={self.user_id}, status={self.account_id})>"
