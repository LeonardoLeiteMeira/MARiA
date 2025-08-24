from collections.abc import Callable
from uuid import UUID
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query

from application import ManagementPeriodApplication
from dto.models import ManagementPeriodDto
from dto import PaginatedDataListDto

from .request_models.management_period import ManagementPeriodRequest, ManagementPeriodFilter


class ManagementPeriodController(APIRouter):
    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], ManagementPeriodApplication]):
        super().__init__(prefix="/management-periods", dependencies=[Depends(jwt_dependency)])

        @self.post("/", response_model=ManagementPeriodDto)
        async def create_period(
            request: Request,
            data: ManagementPeriodRequest,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            return await app.create(data)

        @self.put("/{period_id}")
        async def update_period(
            period_id: UUID,
            request: Request,
            data: ManagementPeriodRequest,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            await app.update(period_id, data)
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/{period_id}")
        async def delete_period(
            period_id: UUID,
            request: Request,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            await app.delete(period_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/{period_id}", response_model=ManagementPeriodDto)
        async def get_period(
            period_id: UUID,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ):
            periods = await app.get_by_ids([period_id])
            if not periods:
                raise HTTPException(status_code=404, detail="management period not found")
            return periods[0]

        PaginatedManagementPeriodDto: TypeAlias = PaginatedDataListDto[ManagementPeriodDto]
        @self.get("/", response_model=PaginatedManagementPeriodDto)
        async def get_periods(
            request: Request,
            app: ManagementPeriodApplication = Depends(app_dependency),
            filter: Annotated[ManagementPeriodFilter, Query()] = None
        ):
            filter.user_id = request.state.user.id
            periods = await app.get_by_filter(filter)
            return periods
