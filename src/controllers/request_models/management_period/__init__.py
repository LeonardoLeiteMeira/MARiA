from datetime import datetime
from uuid import UUID
from typing import Optional, Literal

from pydantic import BaseModel


class ManagementPeriodRequest(BaseModel):
    user_id: UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

class ManagementPeriodFilter(BaseModel):
    user_id: UUID | None = None
    start_date_max: datetime | None = None
    start_date_min: datetime | None = None
    end_date_max: datetime | None = None
    end_date_min: datetime | None = None
    order_start_date: Optional[Literal['desc', 'asc']] = 'desc'
    page: int = 1
    page_size: int = 25
