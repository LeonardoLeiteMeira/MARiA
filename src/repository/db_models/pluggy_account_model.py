import uuid
from typing import Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import String, ForeignKey

from database.configs.base import BaseModel

class PluggyAccountModel(BaseModel):
    __tablename__ = "pluggy_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id'),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    marketing_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    complementary_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<PluggyAccountModel(id={self.id}, user_id={self.user_id}, "
            f"account_id={self.account_id}, name={self.name}, marketing_name={self.marketing_name})>"
        )