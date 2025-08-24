from uuid import UUID
from typing import List, Optional, Literal

from pydantic import BaseModel

class ManagementPlanningRequest(BaseModel):
    user_id: UUID | None = None
    management_period_id: UUID
    planned_value_cents: float
    category_id: UUID | None = None
    name: str | None = None
    tags: List[str] | None = None

class ManagementPlanningFilter(BaseModel):
    user_id: UUID | None = None
    management_period_id: list[str]| None = None
    category_id: list[str]| None = None
    name: str| None = None
    tags: list[str]| None = None
    page: int = 1
    page_size: int = 25