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


class CategoryListResponse(BaseModel):
    """Wrapper for category list responses allowing future metadata expansion."""

    data: list[CategoryResponse]

    model_config = ConfigDict(from_attributes=True)


class MacroCategoryListResponse(BaseModel):
    """Wrapper for macro category list responses enabling pagination metadata."""

    data: list[MacroCategoryResponse]

    model_config = ConfigDict(from_attributes=True)
