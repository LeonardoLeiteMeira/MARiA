from pydantic import BaseModel
from datetime import datetime
from typing import List

from .planning_aggregate import PlanningAggregate

class DashboardAggregate(BaseModel):
    start_period: datetime
    end_period: datetime
    total_incomes: float
    total_expense: float
    total_plan: float
    available_to_plan: float
    total_expenses_out_plan: float
    planning_aggregate: List[PlanningAggregate]