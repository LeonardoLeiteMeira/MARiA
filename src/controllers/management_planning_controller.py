from collections.abc import Callable
from uuid import UUID
from typing import TypeAlias, Annotated, List, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query

from application import ManagementPlanningApplication
from dto.models import ManagementPlanningDto
from dto import PaginatedDataListDto

from .request_models.management_planning import (
    ManagementPlanningRequest,
    ManagementPlanningFilter,
)


class ManagementPlanningController(APIRouter):
    def __init__(
        self,
        jwt_dependency: Callable[..., Any],
        app_dependency: Callable[[], ManagementPlanningApplication],
    ):
        super().__init__(
            prefix="/management-plannings", dependencies=[Depends(jwt_dependency)]
        )

        @self.post("/", response_model=List[ManagementPlanningDto])
        async def create_planning(
            request: Request,
            data: List[ManagementPlanningRequest],
            app: ManagementPlanningApplication = Depends(app_dependency),
        ) -> List[ManagementPlanningDto]:
            user_id = request.state.user.id
            for plan in data:
                plan.user_id = user_id
            return cast(List[ManagementPlanningDto], await app.create(data))

        @self.put("/{planning_id}")
        async def update_planning(
            planning_id: UUID,
            request: Request,
            data: ManagementPlanningRequest,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ) -> Response:
            data.user_id = request.state.user.id
            await app.update(planning_id, data)
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/{planning_id}")
        async def delete_planning(
            planning_id: UUID,
            request: Request,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            await app.delete(planning_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/{planning_id}", response_model=ManagementPlanningDto)
        async def get_planning(
            planning_id: UUID,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ) -> ManagementPlanningDto:
            plannings = await app.get_by_ids([planning_id])
            if not plannings:
                raise HTTPException(status_code=404, detail="planning not found")
            return cast(ManagementPlanningDto, plannings[0])

        PaginatedManagementPlanning: TypeAlias = PaginatedDataListDto[
            ManagementPlanningDto
        ]

        @self.get("/", response_model=PaginatedManagementPlanning)
        async def get_plannings(
            request: Request,
            filter: Annotated[ManagementPlanningFilter, Query()],
            app: ManagementPlanningApplication = Depends(app_dependency),
        ) -> PaginatedManagementPlanning:
            filter.user_id = request.state.user.id
            plannings = await app.get_by_user_id(filter)
            return plannings
