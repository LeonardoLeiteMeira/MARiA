from sqlalchemy.ext.asyncio import AsyncSession
from database import BaseDatabase
from typing import Any

class BaseRepository:
    def __init__(self, base_db: BaseDatabase):
        self.__base_db = base_db

    @property
    def session(self) -> AsyncSession:
        return self.__base_db.session
    
    def apply_pagination(
        self,
        query,
        filters
    ):
        size = filters.page_size
        page = filters.page
        query = query.limit(size).offset((page-1)*size)

        return query
