from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from repository import AccountType


class AccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    type: AccountType
    opening_balance_cents: float
    icon: str | None
    currency: str

    model_config = ConfigDict(from_attributes=True)


class AccountListResponse(BaseModel):
    """Envelope for account collections enabling pagination metadata."""

    data: list[AccountResponse]

    model_config = ConfigDict(from_attributes=True)
