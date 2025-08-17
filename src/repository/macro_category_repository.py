from typing import Sequence
import uuid

from sqlalchemy import select, update, delete

from .base_repository import BaseRepository
from .db_models.macro_category_model import MacroCategoryModel


class MacroCategoryRepository(BaseRepository):
    async def create(self, macro_category: MacroCategoryModel):
        async with self.session() as session:
            session.add(macro_category)
            await session.commit()

    async def update(self, macro_category: MacroCategoryModel):
        if macro_category.id is None:
            raise Exception("macro category id is not defined")
        stmt = (
            update(MacroCategoryModel)
            .where(
                MacroCategoryModel.id == macro_category.id,
                MacroCategoryModel.user_id == macro_category.user_id,
            )
            .values(macro_category)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, macro_category: MacroCategoryModel):
        if macro_category.id is None:
            raise Exception("macro category id is not defined")
        stmt = (
            delete(MacroCategoryModel)
            .where(
                MacroCategoryModel.id == macro_category.id,
                MacroCategoryModel.user_id == macro_category.user_id,
            )
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, macro_category_id: uuid.UUID) -> MacroCategoryModel | None:
        stmt = (
            select(MacroCategoryModel)
            .where(MacroCategoryModel.id == macro_category_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def get_by_ids(self, macro_category_ids: Sequence[uuid.UUID]) -> list[MacroCategoryModel]:
        if not macro_category_ids:
            return []
        stmt = select(MacroCategoryModel).where(MacroCategoryModel.id.in_(macro_category_ids))
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[MacroCategoryModel]:
        stmt = select(MacroCategoryModel).where(MacroCategoryModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
