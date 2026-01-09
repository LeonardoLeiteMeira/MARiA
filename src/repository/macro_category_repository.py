from typing import Sequence, List
import uuid

from sqlalchemy import select, update, delete, inspect

from .base_repository import BaseRepository
from .db_models.macro_category_model import MacroCategoryModel


class MacroCategoryRepository(BaseRepository):
    async def create(self, macro_categories: List[MacroCategoryModel]) -> List[MacroCategoryModel]:
        async with self.session() as session:
            session.add_all(macro_categories)
            await session.commit()
            return macro_categories

    async def update(self, macro_category: MacroCategoryModel) -> None:
        if macro_category.id is None:
            raise Exception("macro category id is not defined")

        mapper = inspect(MacroCategoryModel)
        cols = [c.key for c in mapper.attrs]
        data = {
            c: getattr(macro_category, c)
            for c in cols
            if c not in ("id", "user_id") and getattr(macro_category, c) is not None
        }

        stmt = (
            update(MacroCategoryModel)
            .where(
                MacroCategoryModel.id == macro_category.id,
                MacroCategoryModel.user_id == macro_category.user_id,
            )
            .values(**data)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, macro_category: MacroCategoryModel) -> None:
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
