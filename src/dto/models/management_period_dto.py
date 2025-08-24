from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ManagementPeriodDto(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    start_date: datetime | None
    end_date: datetime | None

    model_config = ConfigDict(from_attributes=True)

