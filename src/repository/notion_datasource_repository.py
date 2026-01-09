from .base_repository import BaseRepository
from .db_models.notion_datasource_model import NotionDatasourceModel

from datetime import datetime
from sqlalchemy import select, update


class NotionDatasourceRepository(BaseRepository):
    async def create_new_datasources(self, new_datasources: list[NotionDatasourceModel]) -> None:
        async with self.session() as session:
            session.add_all(new_datasources)
            await session.commit()

    async def upsert_datasources(self, datasources: list[NotionDatasourceModel]) -> None:
        async with self.session() as session:
            for datasource in datasources:
                stmt = (
                    select(NotionDatasourceModel)
                    .where(NotionDatasourceModel.user_id == datasource.user_id)
                    .where(NotionDatasourceModel.table_id == datasource.table_id)
                )
                cursor = await session.execute(stmt)
                existing = cursor.scalars().first()

                if existing:
                    await session.execute(
                        update(NotionDatasourceModel)
                        .where(NotionDatasourceModel.id == existing.id)
                        .values(
                            table_name=datasource.table_name,
                            tag=datasource.tag,
                            updated_at=datetime.now(),
                        )
                    )
                else:
                    session.add(datasource)

            await session.commit()

    async def get_user_datasources(self, user_id: str) -> list[NotionDatasourceModel]:
        async with self.session() as session:
            stmt = (
                select(NotionDatasourceModel)
                .where(NotionDatasourceModel.user_id == user_id)
                .where(NotionDatasourceModel.tag != None)
            )
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
