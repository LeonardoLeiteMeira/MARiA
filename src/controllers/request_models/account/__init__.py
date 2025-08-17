from uuid import UUID

from pydantic import BaseModel

from repository import AccountType


class AccountRequest(BaseModel):
    """Payload for creating or updating accounts."""

    # Controller sets user based on JWT to avoid tampering
    user_id: UUID | None = None
    type: AccountType
    opening_balance_cents: float
    icon: str | None = None
    currency: str
