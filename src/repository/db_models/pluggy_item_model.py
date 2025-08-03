import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from database.configs.base import BaseModel

class PluggyItemModel(BaseModel):
    __tablename__ = "pluggy_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )
    connector: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    products: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False
    )
    complementary_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    executionStatus: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    lastUpdatedAt: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    connected_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    def __repr__(self):
        return f"<UserItemModel(id={self.id}, user_id={self.user_id}, status={self.status})>"