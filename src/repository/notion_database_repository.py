from .base_repository import BaseRepository
from .db_models.notion_database_model import NotionDatabaseModel

from datetime import datetime

from sqlalchemy import select, update

class NotionDatabaseRepository(BaseRepository):
    async def create_new_databases(self, new_databases: list[NotionDatabaseModel]):
        async with self.session() as session:
            session.add_all(new_databases)
            await session.commit()

    async def upsert_databases(self, databases: list[NotionDatabaseModel]):
        async with self.session() as session:
            for db in databases:
                stmt = (
                    select(NotionDatabaseModel)
                    .where(NotionDatabaseModel.user_id == db.user_id)
                    .where(NotionDatabaseModel.table_id == db.table_id)
                )
                cursor = await session.execute(stmt)
                existing = cursor.scalars().first()

                if existing:
                    await session.execute(
                        update(NotionDatabaseModel)
                        .where(NotionDatabaseModel.id == existing.id)
                        .values(
                            table_name=db.table_name,
                            tag=db.tag,
                            updated_at=datetime.now(),
                        )
                    )
                else:
                    session.add(db)

            await session.commit()

    async def get_user_databases(self, user_id:str) -> list[NotionDatabaseModel]:
        async with self.session() as session:
            stmt = (
                select(NotionDatabaseModel)
                .where(NotionDatabaseModel.user_id == user_id)
                .where(NotionDatabaseModel.tag != None)
            )
            cursor = await session.execute(stmt)
            databases = cursor.scalars().all()
            return databases