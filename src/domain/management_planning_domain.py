from uuid import UUID

from repository import ManagementPlanningRepository, ManagementPlanningModel


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

    async def delete(self, planning_id: UUID) -> None:
        planning = ManagementPlanningModel(id=planning_id)
        await self._repo.delete(planning)

    async def get_by_ids(self, planning_ids: list[UUID]) -> list[ManagementPlanningModel]:
        return await self._repo.get_by_ids(planning_ids)
