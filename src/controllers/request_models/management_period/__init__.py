from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ManagementPeriodRequest(BaseModel):
    """Payload for creating or updating management periods."""

    # user supplied by controller to ensure ownership
    user_id: UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
