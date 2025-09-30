from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
from uuid import UUID

from .planning_aggregate import PlanningAggregate
from .macro_category_transaction_aggregate import MacroCategoryTransactionAggregate
from .category_transaction_aggregate import CategoryTransactionAggregate

class DashboardAggregate(BaseModel):
    management_period_id: UUID
    start_period: datetime
    end_period: datetime
    total_incomes: float
    total_expense: float
    total_plan: float
    available_to_plan: float
    total_expenses_out_plan: float
    planning_aggregate: List[PlanningAggregate]
    expense_by_category: Dict[str, CategoryTransactionAggregate]
    expense_by_macro_category: Dict[str, MacroCategoryTransactionAggregate]