from .base_repository import BaseRepository
from .db_models.pluggy_item_model import PluggyItemModel

from sqlalchemy import text, Column, String, Integer, select, update, delete, desc

class PluggyItemRepository(BaseRepository):
    async def get_pluggy_item_by_item_id(self, item_id: str) -> PluggyItemModel | None:
        stmt = (
            select(PluggyItemModel)
            .where(PluggyItemModel.item_id == item_id) 
            .execution_options(synchronize_session="fetch")
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()
        
    async def create_pluggy_item(self, new_pluggy_item: PluggyItemModel):
        async with self.session() as session:
            session.add(new_pluggy_item)
            await session.commit()
