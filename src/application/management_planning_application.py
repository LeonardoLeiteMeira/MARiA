from uuid import UUID
from typing import TYPE_CHECKING, List

from domain import ManagementPlanningDomain
from repository import ManagementPlanningModel
from dto.models import ManagementPlanningDto
from dto import PaginatedDataListDto

if TYPE_CHECKING:
    from controllers.request_models.management_planning import ManagementPlanningRequest, ManagementPlanningFilter


class ManagementPlanningApplication:
    """Application layer for management planning features."""

    def __init__(self, domain: ManagementPlanningDomain):
        self._domain = domain

    async def create(self, plan: List["ManagementPlanningRequest"]) -> ManagementPlanningModel:
        planning = [ManagementPlanningModel(**(data.model_dump())) for data in plan]
        return await self._domain.create(planning)

    async def update(self, planning_id: UUID, data: "ManagementPlanningRequest") -> ManagementPlanningModel:
        planning = ManagementPlanningModel(**(data.model_dump()))
        planning.id = planning_id
        return await self._domain.update(planning)

    async def delete(self, planning_id: UUID, user_id: UUID) -> None:
        await self._domain.delete(planning_id, user_id)

    async def get_by_ids(self, planning_ids: list[UUID]) -> list[ManagementPlanningModel]:
        return await self._domain.get_by_ids(planning_ids)

    async def get_by_user_id(self, filter: 'ManagementPlanningFilter') -> PaginatedDataListDto[ManagementPlanningDto]:
        return await self._domain.get_by_user_id(filter)
