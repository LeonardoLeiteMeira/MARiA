from uuid import UUID
from typing import TYPE_CHECKING

from domain import ManagementPeriodDomain
from repository import ManagementPeriodModel

if TYPE_CHECKING:
    from controllers.request_models.management_period import ManagementPeriodRequest


class ManagementPeriodApplication:
    """Application layer for management period.

    All business validations should be placed here before delegating to the
    domain layer. For now it simply forwards the calls."""

    def __init__(self, domain: ManagementPeriodDomain):
        self._domain = domain

    async def create(self, data: "ManagementPeriodRequest") -> ManagementPeriodModel:
        period = ManagementPeriodModel(
            user_id=data.user_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return await self._domain.create(period)

    async def update(self, period_id: UUID, data: "ManagementPeriodRequest") -> ManagementPeriodModel:
        period = ManagementPeriodModel(
            id=period_id,
            user_id=data.user_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return await self._domain.update(period)

    async def delete(self, period_id: UUID) -> None:
        await self._domain.delete(period_id)

    async def get_by_ids(self, period_ids: list[UUID]) -> list[ManagementPeriodModel]:
        return await self._domain.get_by_ids(period_ids)
