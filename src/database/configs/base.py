from sqlalchemy.orm import attributes
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class BaseModel(Base, AsyncAttrs):
    __abstract__ = True

    def is_attr_loaded(self, attr_name: str) -> bool:
        return attributes.is_attribute_loaded(self, attr_name)