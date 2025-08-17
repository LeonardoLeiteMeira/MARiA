from typing import Sequence
import uuid

from sqlalchemy import select, update, delete

from .base_repository import BaseRepository
from .db_models.category_model import CategoryModel


class CategoryRepository(BaseRepository):
    async def create(self, category: CategoryModel):
        async with self.session() as session:
            session.add(category)
            await session.commit()

    async def update(self, category: CategoryModel):
        if category.id is None:
            raise Exception("category id is not defined")
        stmt = (
            update(CategoryModel)
            .where(CategoryModel.id == category.id)
            .values(category)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, category: CategoryModel):
        if category.id is None:
            raise Exception("category id is not defined")
        stmt = (
            delete(CategoryModel)
            .where(CategoryModel.id == category.id)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, category_id: uuid.UUID) -> CategoryModel | None:
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.id == category_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def get_by_ids(self, category_ids: Sequence[uuid.UUID]) -> list[CategoryModel]:
        if not category_ids:
            return []
        stmt = select(CategoryModel).where(CategoryModel.id.in_(category_ids))
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[CategoryModel]:
        stmt = select(CategoryModel).where(CategoryModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
