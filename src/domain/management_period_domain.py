from uuid import UUID
from typing import TYPE_CHECKING

from repository import ManagementPeriodRepository, ManagementPeriodModel
from dto import PaginatedDataListDto
from dto.models import ManagementPeriodDto

if TYPE_CHECKING:
    from controllers.request_models.management_period import ManagementPeriodFilter


class ManagementPeriodDomain:
    """Domain layer for management period operations.

    This layer is responsible for translating raw data into database models
    and delegating persistence to the repository. Any business rules that
    belong specifically to management periods should live here, but for now
    it only prepares the SQLAlchemy models."""

    def __init__(self, repo: ManagementPeriodRepository):
        self._repo = repo

    async def create(self, period: ManagementPeriodModel) -> ManagementPeriodModel:
        await self._repo.create(period)
        return period

    async def update(self, period: ManagementPeriodModel) -> ManagementPeriodModel:
        await self._repo.update(period)
        return period

    async def delete(self, period_id: UUID, user_id: UUID) -> None:
        period = ManagementPeriodModel(id=period_id, user_id=user_id)
        await self._repo.delete(period)

    async def get_by_ids(self, period_ids: list[UUID]) -> list[ManagementPeriodModel]:
        return await self._repo.get_by_ids(period_ids)

    async def get_by_filter(self, filter: 'ManagementPeriodFilter') -> PaginatedDataListDto[ManagementPeriodDto]:
        return await self._repo.get_by_filter(filter)
