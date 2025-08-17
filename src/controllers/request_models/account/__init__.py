from uuid import UUID

from pydantic import BaseModel

from repository import AccountType


class AccountRequest(BaseModel):
    """Payload for creating or updating accounts."""

    user_id: UUID
    type: AccountType
    opening_balance_cents: float
    icon: str | None = None
    currency: str
