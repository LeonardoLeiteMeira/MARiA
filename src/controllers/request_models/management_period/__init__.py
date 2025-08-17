from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ManagementPeriodRequest(BaseModel):
    """Payload for creating or updating management periods."""

    user_id: UUID
    start_date: datetime | None = None
    end_date: datetime | None = None
