from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from repository.db_models.account_model import AccountType

class AccountWithBalanceAggregate(BaseModel):
    id: UUID
    user_id: UUID
    type: AccountType
    opening_balance_cents: float
    icon: str | None
    currency: str
    name: str | None
    balance: float
    balance_date: datetime