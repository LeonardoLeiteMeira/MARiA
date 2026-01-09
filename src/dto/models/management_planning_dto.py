from datetime import datetime
from uuid import UUID
from typing import List
from pydantic import BaseModel, ConfigDict


class ManagementPlanningDto(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    category_id: UUID | None
    planned_value_cents: float
    management_period_id: UUID
    name: str | None
    tags: List[str] | None

    model_config = ConfigDict(from_attributes=True)
