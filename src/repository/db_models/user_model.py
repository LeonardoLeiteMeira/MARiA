from database.configs.base import Base
from sqlalchemy import String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from repository import ThreadModel, NotionAuthorizationModel, NotionDatasourceModel


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    enable: Mapped[str] = mapped_column(Boolean, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at:Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at:Mapped[datetime] = mapped_column(TIMESTAMP,  default=datetime.now, onupdate=datetime.now)

    threads:Mapped[list['ThreadModel']] = relationship(backref='threads', lazy='noload') # type: ignore
    notion_authorization:Mapped['NotionAuthorizationModel'] = relationship(backref='notion_authorizations', lazy='noload', uselist=False) # type: ignore
    notion_datasources: Mapped[list['NotionDatasourceModel']] = relationship(backref='notion_datasources', lazy='noload')  # type: ignore

    def __repr__(self):
        return f"{self.id} - {self.name} - {self.email} "
