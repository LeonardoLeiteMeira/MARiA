from collections.abc import Callable
from uuid import UUID
from typing import Annotated, Any, cast, TypeAlias

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    Query,
    Response,
)

from application import ManagementPeriodApplication
from dto.aggregates import DashboardAggregate
from dto.models import ManagementPeriodDto
from dto import PaginatedDataListDto

from .request_models.management_period import (
    ManagementPeriodRequest,
    ManagementPeriodFilter,
)


class ManagementPeriodController(APIRouter):
    def __init__(
        self,
        jwt_dependency: Callable[..., Any],
        app_dependency: Callable[[], ManagementPeriodApplication],
    ):
        super().__init__(
            prefix="/management-periods", dependencies=[Depends(jwt_dependency)]
        )

        @self.post("", response_model=ManagementPeriodDto)
        async def create_period(
            request: Request,
            data: ManagementPeriodRequest,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ) -> ManagementPeriodDto:
            data.user_id = request.state.user.id
            return cast(ManagementPeriodDto, await app.create(data))

        @self.get("/resume", response_model=DashboardAggregate)
        async def get_resume_current_period(
            request: Request,
            period_id: Annotated[UUID | None, Query()] = None,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ) -> DashboardAggregate:
            user_id = request.state.user.id
            return await app.get_current_period_resume(user_id, period_id)

        @self.put("/{period_id}")
        async def update_period(
            period_id: UUID,
            request: Request,
            data: ManagementPeriodRequest,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ) -> Response:
            data.user_id = request.state.user.id
            await app.update(period_id, data)
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/{period_id}")
        async def delete_period(
            period_id: UUID,
            request: Request,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            await app.delete(period_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/{period_id}", response_model=ManagementPeriodDto)
        async def get_period(
            period_id: UUID,
            request: Request,
            app: ManagementPeriodApplication = Depends(app_dependency),
        ) -> ManagementPeriodDto:
            user_id = request.state.user.id
            periods = await app.get_by_ids([period_id], user_id)
            if not periods:
                raise HTTPException(
                    status_code=404, detail="management period not found"
                )
            return cast(ManagementPeriodDto, periods[0])

        PaginatedManagementPeriodDto: TypeAlias = PaginatedDataListDto[
            ManagementPeriodDto
        ]

        @self.get("", response_model=PaginatedManagementPeriodDto)
        async def get_periods(
            request: Request,
            filter: Annotated[ManagementPeriodFilter, Query()],
            app: ManagementPeriodApplication = Depends(app_dependency),
        ) -> PaginatedManagementPeriodDto:
            filter.user_id = request.state.user.id
            periods = await app.get_by_filter(filter)
            return periods
