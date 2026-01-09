from pydantic import BaseModel
from uuid import UUID
from typing import List

from ..models.transaction_dto import TransactionDto


class PlanningAggregate(BaseModel):
    plan_id: UUID
    category_id: UUID
    plan_value_cents: float
    total_expenses: float
    total_available: float
    name: str | None
    category_name: str
    category_icon: str | None
    transactions: List[TransactionDto]
