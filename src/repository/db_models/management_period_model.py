import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from database.configs.base import BaseModel


class ManagementPeriodModel(BaseModel):
    __tablename__ = "management_period"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now, onupdate=datetime.now
    )
    start_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)
