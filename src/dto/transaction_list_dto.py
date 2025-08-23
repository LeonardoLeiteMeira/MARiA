from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from repository.db_models.transaction_model import TransactionModel

@dataclass
class TransactionListDto:
    total_count: str
    page: int
    page_size: int
    transactions: List['TransactionModel'] = field(default_factory=list)