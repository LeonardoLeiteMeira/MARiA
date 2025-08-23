from datetime import datetime
from uuid import UUID
from typing import List

from pydantic import BaseModel

from repository import TransactionType


class TransactionRequest(BaseModel):
    user_id: UUID | None = None
    name: str
    amount_cents: float
    occurred_at: datetime
    category_id: UUID | None = None
    macro_category_id: UUID | None = None
    type: TransactionType
    management_period_id: UUID
    source_account_id: UUID | None = None
    destination_account_id: UUID | None = None
    tags: List[str] | None = None
    currency: str


class TransactionFilter(BaseModel):
    user_id: UUID = None
    tags: list[str] = None
    destination_account_id: list[str] = None
    source_account_id: list[str] = None
    management_period_id: list[str] = None
    type: list[TransactionType] = None
    macro_category_id: list[str] = None
    category_id: list[str] = None
    occurred_at_from: datetime = None
    occurred_at_to: datetime = None
    min_amount: float = None
    max_amount: float = None
    name: str = None


