from datetime import datetime
from uuid import UUID
from typing import List, Optional, Literal

from pydantic import BaseModel

from dto.models import TransactionType


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
    destination_account_id: list[UUID] = None
    source_account_id: list[UUID] = None
    any_accounts_id: list[UUID] = None
    management_period_id: list[UUID] = None
    type: list[TransactionType] = None
    macro_category_id: list[UUID] = None
    category_id: list[UUID] = None
    occurred_at_min: datetime = None
    occurred_at_max: datetime = None
    min_amount: float = None
    max_amount: float = None
    name: str = None
    sort_order: Optional[Literal["asc", "desc"]] = "desc"
    page: int = 1
    page_size: int = 25


