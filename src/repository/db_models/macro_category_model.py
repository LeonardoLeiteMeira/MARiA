import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from database.configs.base import BaseModel


class MacroCategoryModel(BaseModel):
    __tablename__ = 'macro_categories'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.now,
        onupdate=datetime.now
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    icon: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
