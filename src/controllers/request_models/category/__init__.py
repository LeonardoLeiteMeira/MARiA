from uuid import UUID

from pydantic import BaseModel


class CategoryRequest(BaseModel):
    """Payload for creating or updating categories or macro categories."""

    user_id: UUID
    name: str
    icon: str | None = None
