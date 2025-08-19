from typing import Sequence
import uuid

from sqlalchemy import select, update, delete, inspect

from .base_repository import BaseRepository
from .db_models.management_period_model import ManagementPeriodModel


class ManagementPeriodRepository(BaseRepository):
    async def create(self, management_period: ManagementPeriodModel):
        async with self.session() as session:
            session.add(management_period)
            await session.commit()

    async def update(self, management_period: ManagementPeriodModel):
        if management_period.id is None:
            raise Exception("management period id is not defined")

        mapper = inspect(ManagementPeriodModel)
        cols = [c.key for c in mapper.attrs]
        data = {
            c: getattr(management_period, c)
            for c in cols
            if c not in ("id", "user_id") and getattr(management_period, c) is not None
        }

        stmt = (
            update(ManagementPeriodModel)
            .where(
                ManagementPeriodModel.id == management_period.id,
                ManagementPeriodModel.user_id == management_period.user_id,
            )
            .values(**data)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, management_period: ManagementPeriodModel):
        if management_period.id is None:
            raise Exception("management period id is not defined")
        stmt = (
            delete(ManagementPeriodModel)
            .where(
                ManagementPeriodModel.id == management_period.id,
                ManagementPeriodModel.user_id == management_period.user_id,
            )
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, management_period_id: uuid.UUID) -> ManagementPeriodModel | None:
        stmt = (
            select(ManagementPeriodModel)
            .where(ManagementPeriodModel.id == management_period_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def get_by_ids(self, management_period_ids: Sequence[uuid.UUID]) -> list[ManagementPeriodModel]:
        if not management_period_ids:
            return []
        stmt = select(ManagementPeriodModel).where(ManagementPeriodModel.id.in_(management_period_ids))
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[ManagementPeriodModel]:
        stmt = select(ManagementPeriodModel).where(ManagementPeriodModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
