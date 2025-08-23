from datetime import datetime
from uuid import UUID
from typing import List
from pydantic import BaseModel, ConfigDict

from repository import TransactionType


class TransactionResponse(BaseModel):
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


class TransactionListResponse(BaseModel):
    """Envelope for transaction list responses enabling future pagination metadata."""

    data: list[TransactionResponse]
    page: int
    page_size: int
    total_count: int

    model_config = ConfigDict(from_attributes=True)
