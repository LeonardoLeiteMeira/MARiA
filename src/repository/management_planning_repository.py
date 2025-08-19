from typing import Sequence
import uuid

from sqlalchemy import select, update, delete, inspect

from .base_repository import BaseRepository
from .db_models.management_planning_model import ManagementPlanningModel


class ManagementPlanningRepository(BaseRepository):
    async def create(self, planning: ManagementPlanningModel):
        async with self.session() as session:
            session.add(planning)
            await session.commit()

    async def update(self, planning: ManagementPlanningModel):
        if planning.id is None:
            raise Exception("management planning id is not defined")

        mapper = inspect(ManagementPlanningModel)
        cols = [c.key for c in mapper.attrs]
        data = {
            c: getattr(planning, c)
            for c in cols
            if c not in ("id", "user_id") and getattr(planning, c) is not None
        }

        stmt = (
            update(ManagementPlanningModel)
            .where(
                ManagementPlanningModel.id == planning.id,
                ManagementPlanningModel.user_id == planning.user_id,
            )
            .values(**data)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, planning: ManagementPlanningModel):
        if planning.id is None:
            raise Exception("management planning id is not defined")
        stmt = (
            delete(ManagementPlanningModel)
            .where(
                ManagementPlanningModel.id == planning.id,
                ManagementPlanningModel.user_id == planning.user_id,
            )
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, planning_id: uuid.UUID) -> ManagementPlanningModel | None:
        stmt = (
            select(ManagementPlanningModel)
            .where(ManagementPlanningModel.id == planning_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def get_by_ids(self, planning_ids: Sequence[uuid.UUID]) -> list[ManagementPlanningModel]:
        if not planning_ids:
            return []
        stmt = select(ManagementPlanningModel).where(ManagementPlanningModel.id.in_(planning_ids))
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[ManagementPlanningModel]:
        stmt = select(ManagementPlanningModel).where(ManagementPlanningModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
