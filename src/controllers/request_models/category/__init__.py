from uuid import UUID

from pydantic import BaseModel


class CategoryRequest(BaseModel):
    """Payload for creating or updating categories or macro categories."""

    name: str
    user_id: UUID | None = None
    icon: str | None = None
