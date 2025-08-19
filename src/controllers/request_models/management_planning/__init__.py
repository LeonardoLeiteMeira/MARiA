from uuid import UUID
from typing import List

from pydantic import BaseModel


class ManagementPlanningRequest(BaseModel):
    """Payload for creating or updating management plannings."""

    # Controller injects user context to preserve access control
    user_id: UUID | None = None
    management_period_id: UUID
    planned_value_cents: float
    category_id: UUID | None = None
    name: str | None = None
    tags: List[str] | None = None
