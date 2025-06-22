from .base_repository import BaseRepository
from .db_models.notion_database_model import NotionDatabaseModel, UserModel

from sqlalchemy import text, Column, String, Integer, select, update, delete, desc

class NotionDatabaseRepository(BaseRepository):
    async def create_new_databases(self, new_databases: list[NotionDatabaseModel]):
        async with self.session() as session:
            session.add_all(new_databases)
            await session.commit()

    async def get_user_databases(self, user_id:str):
        async with self.session() as session:
            stmt = (
                select(NotionDatabaseModel)
                .where(NotionDatabaseModel.user_id == user_id)
            )
            cursor = await session.execute(stmt)
            databases = cursor.scalars().all()
            return databases