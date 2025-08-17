from uuid import UUID
from typing import TYPE_CHECKING

from domain import ManagementPlanningDomain
from repository import ManagementPlanningModel

if TYPE_CHECKING:
    from controllers.request_models.management_planning import ManagementPlanningRequest


class ManagementPlanningApplication:
    """Application layer for management planning features."""

    def __init__(self, domain: ManagementPlanningDomain):
        self._domain = domain

    async def create(self, data: "ManagementPlanningRequest") -> ManagementPlanningModel:
        planning = ManagementPlanningModel(
            user_id=data.user_id,
            management_period_id=data.management_period_id,
            planned_value_cents=data.planned_value_cents,
            category_id=data.category_id,
            name=data.name,
            tags=data.tags,
        )
        return await self._domain.create(planning)

    async def update(self, planning_id: UUID, data: "ManagementPlanningRequest") -> ManagementPlanningModel:
        planning = ManagementPlanningModel(
            id=planning_id,
            user_id=data.user_id,
            management_period_id=data.management_period_id,
            planned_value_cents=data.planned_value_cents,
            category_id=data.category_id,
            name=data.name,
            tags=data.tags,
        )
        return await self._domain.update(planning)

    async def delete(self, planning_id: UUID) -> None:
        await self._domain.delete(planning_id)

    async def get_by_ids(self, planning_ids: list[UUID]) -> list[ManagementPlanningModel]:
        return await self._domain.get_by_ids(planning_ids)
