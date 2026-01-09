import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import TIMESTAMP, String, ForeignKey, Numeric, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from database.configs.base import BaseModel


class AccountType(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    WALLET = "WALLET"


class AccountModel(BaseModel):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now, onupdate=datetime.now
    )
    type: Mapped[AccountType] = mapped_column(
        SqlEnum(AccountType, name="user_account_type"), nullable=False
    )
    opening_balance_cents: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    icon: Mapped[str | None] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(5), nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=None)
