from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    icon: str | None

    model_config = ConfigDict(from_attributes=True)


class MacroCategoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    name: str
    icon: str | None

    model_config = ConfigDict(from_attributes=True)
