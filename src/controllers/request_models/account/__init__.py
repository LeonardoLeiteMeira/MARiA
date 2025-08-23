from uuid import UUID

from pydantic import BaseModel

from repository import AccountType


class AccountRequest(BaseModel):
    user_id: UUID | None = None
    type: AccountType
    opening_balance_cents: float
    icon: str | None = None
    currency: str
