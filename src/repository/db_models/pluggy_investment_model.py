import uuid
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from sqlalchemy import String, ForeignKey

from database.configs.base import BaseModel


class PluggyInvestmentModel(BaseModel):
    __tablename__ = "pluggy_investments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    code: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    subtype: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    balance: Mapped[float] = mapped_column(
        NUMERIC,
        nullable=False,
    )
    complementary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<PluggyInvestmentModel(id={self.id}, user_id={self.user_id}, name={self.name}, type={self.type})>"
        )
