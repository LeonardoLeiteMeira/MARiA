from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from database import BaseDatabase


class BaseRepository:
    def __init__(self, base_db: BaseDatabase) -> None:
        self.__base_db = base_db

    @property
    def session(self) -> Callable[[], AsyncSession]:
        return self.__base_db.session

    def apply_pagination(
        self,
        query: Any,
        filters: Any,
    ) -> Any:
        size = filters.page_size
        page = filters.page
        query = query.limit(size).offset((page - 1) * size)

        return query
