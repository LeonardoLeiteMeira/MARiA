from database.configs.base import Base
from sqlalchemy import text, Column, String, Integer, select, update, delete, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    accepts_communications:Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    phone_number:Mapped[str] = mapped_column(String, nullable=False)
    created_at:Mapped[datetime] = mapped_column(TIMESTAMP)
    updated_at:Mapped[datetime] = mapped_column(TIMESTAMP)

    threads:Mapped[list["ThreadModel"]] = relationship(backref='threads', lazy='noload')

    def __repr__(self):
        return f"{self.id} - {self.name} - {self.email} "