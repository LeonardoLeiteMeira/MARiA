from pydantic import BaseModel, ConfigDict
from typing import List
from uuid import UUID
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    TRANSFER = 'TRANSFER'

class TransactionDto(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    amount_cents: float
    occurred_at: datetime
    category_id: UUID | None
    macro_category_id: UUID | None
    type: TransactionType
    management_period_id: UUID
    source_account_id: UUID | None
    destination_account_id: UUID | None
    tags: List[str] | None
    currency: str

    model_config = ConfigDict(from_attributes=True)