from uuid import UUID

from pydantic import BaseModel


class CategoryRequest(BaseModel):
    """Payload for creating or updating categories or macro categories."""

    # user is injected by controller to prevent spoofing another account
    user_id: UUID | None = None
    name: str
    icon: str | None = None
