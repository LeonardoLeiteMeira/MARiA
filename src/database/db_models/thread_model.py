from database.configs.base import Base
from sqlalchemy import ForeignKey, Column, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID

class ThreadModel(Base):
    __tablename__ = 'threads'

    thread_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP)
    status = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP) 
    is_active = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"{self.thread_id} - {self.user_id}"