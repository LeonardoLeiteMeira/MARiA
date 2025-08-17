from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from application import ManagementPeriodApplication
from .request_models.management_period import ManagementPeriodRequest
from .response_models.management_period import ManagementPeriodResponse


class ManagementPeriodController(APIRouter):
    """HTTP interface for management period operations."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], ManagementPeriodApplication]):
        # Apply JWT authentication to all routes
        super().__init__(prefix="/management-periods", dependencies=[Depends(jwt_dependency)])

        @self.post("/", response_model=ManagementPeriodResponse)
        async def create_period(
            data: ManagementPeriodRequest,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            return await app.create(data)

        @self.put("/{period_id}", response_model=ManagementPeriodResponse)
        async def update_period(
            period_id: UUID,
            data: ManagementPeriodRequest,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            return await app.update(period_id, data)

        @self.delete("/{period_id}")
        async def delete_period(
            period_id: UUID,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            await app.delete(period_id)
            return {"detail": "deleted"}

        @self.get("/{period_id}", response_model=ManagementPeriodResponse)
        async def get_period(
            period_id: UUID,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            periods = await app.get_by_ids([period_id])
            if not periods:
                raise HTTPException(status_code=404, detail="management period not found")
            return periods[0]

        @self.get("/", response_model=list[ManagementPeriodResponse])
        async def get_periods(
            ids: list[UUID] | None = Query(default=None),
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            ids = ids or []
            return await app.get_by_ids(ids)
