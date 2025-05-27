from database.base_database import BaseDatabase

class BaseRepository:
    def __init__(self, base_db: BaseDatabase):
        self._base_db = base_db

    async def _execute_in_transaction(self, func, *args, **kwargs):
        trans = await self._base_db.session.begin()
        try:
            result = await func(*args, **kwargs)
            await trans.commit()
            return result
        except Exception as err:
            await trans.rollback()
            print("Ocorreu um erro:", err)
            raise