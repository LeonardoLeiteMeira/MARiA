from typing import List
from pydantic import BaseModel
from uuid import UUID

from ..models.transaction_dto import TransactionDto


class MacroCategoryTransactionAggregate(BaseModel):
    macro_category_id: UUID
    total: float
    transactions: List[TransactionDto]
    macro_category_name: str
    icon: str | None
