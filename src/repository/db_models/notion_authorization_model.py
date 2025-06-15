import enum
import uuid
from datetime import datetime
from secrets import decrypt, encrypt

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.configs.base import Base


class OwnerType(enum.Enum):
    workspace = "workspace"
    user = "user"


class NotionAuthorizationModel(Base):
    __tablename__ = "notion_authorizations"
    __table_args__ = (UniqueConstraint("bot_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    bot_id: Mapped[str] = mapped_column(String, nullable=False)
    _access_token: Mapped[str] = mapped_column("access_token", String, nullable=False)
    workspace_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_name: Mapped[str] = mapped_column(String, nullable=False)
    workspace_icon: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_type: Mapped[OwnerType] = mapped_column(SAEnum(OwnerType), nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def access_token(self) -> str:
        return decrypt(self._access_token)

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = encrypt(value)
