from uuid import UUID
from typing import List

from pydantic import BaseModel


class ManagementPlanningRequest(BaseModel):
    """Payload for creating or updating management plannings."""

    user_id: UUID
    management_period_id: UUID
    planned_value_cents: float
    category_id: UUID | None = None
    name: str | None = None
    tags: List[str] | None = None
