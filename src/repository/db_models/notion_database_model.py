from database.configs.base import Base
from sqlalchemy import String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class NotionDatabaseModel(Base):
    __tablename__ = 'notion_databases'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id:Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    table_name: Mapped[str] = mapped_column(String(length=123), nullable=False)
    table_id: Mapped[str] = mapped_column(String(), nullable=False)
    tag: Mapped[str] = mapped_column(String(), nullable=True)
    created_at:Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at:Mapped[datetime] = mapped_column(TIMESTAMP,  default=datetime.now, onupdate=datetime.now)

    user = relationship("UserModel", back_populates="notion_authorization")

    def __repr__(self):
        return f"{self.table_name} - {self.tag} - {self.table_id} "