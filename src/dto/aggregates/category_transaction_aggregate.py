from typing import List
from pydantic import BaseModel
from uuid import UUID

from ..models.transaction_dto import TransactionDto

class CategoryTransactionAggregate(BaseModel):
    category_id: UUID
    total: float
    transactions: List[TransactionDto]
    category_name: str
    icon: str | None
    plan_value: float | None
    plan_name: str | str