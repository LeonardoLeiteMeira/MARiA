from datetime import datetime
from uuid import UUID
from typing import List

from pydantic import BaseModel

from repository import TransactionType


class TransactionRequest(BaseModel):
    """Payload for creating or updating transactions."""

    user_id: UUID
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
