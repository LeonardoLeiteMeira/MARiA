from database.configs.base import Base
from sqlalchemy import ForeignKey, Column, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime

class ThreadModel(Base):
    __tablename__ = 'threads'

    thread_id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id:Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at:Mapped[datetime] = mapped_column(TIMESTAMP)
    status:Mapped[str] = mapped_column(String, nullable=False)
    updated_at:Mapped[datetime] = mapped_column(TIMESTAMP) 
    is_active:Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self):
        return f"{self.thread_id} - {self.user_id}"