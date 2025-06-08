from sqlalchemy.ext.asyncio import AsyncSession
from database.base_database import BaseDatabase

class BaseRepository:
    def __init__(self, base_db: BaseDatabase):
        self.__base_db = base_db

    @property
    def session(self) -> AsyncSession:
        return self.__base_db.session
