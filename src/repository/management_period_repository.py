from typing import Sequence
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select, update, delete, inspect, func

from dto import PaginatedDataListDto
from dto.models import ManagementPeriodDto

if TYPE_CHECKING:
    from controllers.request_models.management_period import ManagementPeriodFilter

from .base_repository import BaseRepository
from .db_models.management_period_model import ManagementPeriodModel
from .mixin import ManagementPeriodFilterToSqlAlchemyMixin


class ManagementPeriodRepository(BaseRepository, ManagementPeriodFilterToSqlAlchemyMixin):
    async def create(self, management_period: ManagementPeriodModel) -> None:
        async with self.session() as session:
            session.add(management_period)
            await session.commit()

    async def update(self, management_period: ManagementPeriodModel) -> None:
        if management_period.id is None:
            raise Exception("management period id is not defined")

        mapper = inspect(ManagementPeriodModel)
        columns = [column.key for column in mapper.attrs]
        data = {
            column: getattr(management_period, column)
            for column in columns
            if column not in ("id", "user_id") and getattr(management_period, column) is not None
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

    async def delete(self, management_period: ManagementPeriodModel) -> None:
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

    async def get_by_ids(self, management_period_ids: Sequence[uuid.UUID], user_id: uuid.UUID) -> list[ManagementPeriodModel]:
        if not management_period_ids:
            return []
        stmt = (select(ManagementPeriodModel)
                .where(
                    ManagementPeriodModel.id.in_(management_period_ids),
                    ManagementPeriodModel.user_id == user_id,
                )
            )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_by_filter(self, filter: 'ManagementPeriodFilter') -> PaginatedDataListDto[ManagementPeriodDto]:
        stmt = select(ManagementPeriodModel)
        stmt = self.apply_filters(stmt, filter, ManagementPeriodModel)
        async with self.session() as session:
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total_count = total_result.scalar_one()

            stmt = self.apply_pagination(stmt, filter)
            cursor = await session.execute(stmt)
            management_period_list = list(cursor.scalars().all())

            management_period_list_dto = [ManagementPeriodDto.model_validate(model) for model in management_period_list]

            return PaginatedDataListDto(
                list_data=management_period_list_dto,
                page=filter.page,
                page_size=len(management_period_list),
                total_count=total_count,
            )

            
