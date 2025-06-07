from database.configs.base import Base
from sqlalchemy import text, Column, String, Integer, select, update, delete, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    accepts_communications = Column(Boolean, nullable=False, default=False)
    phone_number = Column(String, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    threads = relationship('ThreadModel', backref='threads', lazy='noload')

    def __repr__(self):
        return f"{self.id} - {self.name} - {self.email} "