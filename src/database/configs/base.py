from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, attributes


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    def is_attr_loaded(self, attr_name: str) -> bool:
        return bool(attributes.is_attribute_loaded(self, attr_name))  # type: ignore[attr-defined]
