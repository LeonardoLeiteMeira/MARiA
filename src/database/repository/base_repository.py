from database.base_database import BaseDatabase

class BaseRepository:
    def __init__(self, base_db: BaseDatabase):
        self._base_db = base_db
