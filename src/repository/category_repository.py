from typing import Sequence, List
import uuid

from sqlalchemy import select, update, delete, inspect

from .base_repository import BaseRepository
from .db_models.category_model import CategoryModel


class CategoryRepository(BaseRepository):
    async def create(self, categories: List[CategoryModel]) -> List[CategoryModel]:
        async with self.session() as session:
            session.add_all(categories)
            await session.commit()
            return categories

    async def update(self, category: CategoryModel):
        if category.id is None:
            raise Exception("category id is not defined")

        # Build dict of updatable fields, ignoring identifiers and nulls
        mapper = inspect(CategoryModel)
        cols = [c.key for c in mapper.attrs]
        data = {
            c: getattr(category, c)
            for c in cols
            if c not in ("id", "user_id") and getattr(category, c) is not None
        }

        stmt = (
            update(CategoryModel)
            .where(
                CategoryModel.id == category.id,
                CategoryModel.user_id == category.user_id,
            )
            .values(**data)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, category: CategoryModel):
        if category.id is None:
            raise Exception("category id is not defined")
        stmt = (
            delete(CategoryModel)
            .where(
                CategoryModel.id == category.id,
                CategoryModel.user_id == category.user_id,
            )
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
