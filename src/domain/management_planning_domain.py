from uuid import UUID
from typing import TYPE_CHECKING

from repository import ManagementPlanningRepository, ManagementPlanningModel
from dto.models import ManagementPlanningDto
from dto import PaginatedDataListDto

if TYPE_CHECKING:
    from controllers.request_models.management_planning import ManagementPlanningFilter


class ManagementPlanningDomain:
    """Domain layer for management planning operations."""

    def __init__(self, repo: ManagementPlanningRepository):
        self._repo = repo

    async def create(self, planning: ManagementPlanningModel) -> ManagementPlanningModel:
        await self._repo.create(planning)
        return planning

    async def update(self, planning: ManagementPlanningModel) -> ManagementPlanningModel:
        await self._repo.update(planning)
        return planning

    async def delete(self, planning_id: UUID, user_id: UUID) -> None:
        planning = ManagementPlanningModel(id=planning_id, user_id=user_id)
        await self._repo.delete(planning)

    async def get_by_ids(self, planning_ids: list[UUID]) -> list[ManagementPlanningModel]:
        return await self._repo.get_by_ids(planning_ids)

    async def get_by_user_id(self, filter: 'ManagementPlanningFilter') -> PaginatedDataListDto[ManagementPlanningDto]:
        return await self._repo.get_by_user_id(filter)
