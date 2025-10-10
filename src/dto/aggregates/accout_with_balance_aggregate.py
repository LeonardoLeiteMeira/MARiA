from pydantic import BaseModel, ConfigDict, Field
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
    balance_cents: float|None = 0
    balance_date: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)