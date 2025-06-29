from database.configs.base import Base
from sqlalchemy import ForeignKey, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from datetime import datetime

class ThreadModel(Base):
    __tablename__ = 'threads'

    id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id:Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at:Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at:Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now, onupdate=datetime.now) 

    def __repr__(self):
        return f"Id:{self.id} - UserId{self.user_id}"