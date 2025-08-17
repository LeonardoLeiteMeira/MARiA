from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from application import ManagementPlanningApplication
from .request_models.management_planning import ManagementPlanningRequest
from .response_models.management_planning import ManagementPlanningResponse


class ManagementPlanningController(APIRouter):
    """Controller exposing management planning operations."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], ManagementPlanningApplication]):
        super().__init__(prefix="/management-plannings", dependencies=[Depends(jwt_dependency)])

        @self.post("/", response_model=ManagementPlanningResponse)
        async def create_planning(
            request: Request,
            data: ManagementPlanningRequest,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ):
            # assign authenticated user to planning payload
            data.user_id = request.state.user.id
            return await app.create(data)

        @self.put("/{planning_id}", response_model=ManagementPlanningResponse)
        async def update_planning(
            planning_id: UUID,
            request: Request,
            data: ManagementPlanningRequest,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            return await app.update(planning_id, data)

        @self.delete("/{planning_id}")
        async def delete_planning(
            planning_id: UUID,
            request: Request,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ):
            await app.delete(planning_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/{planning_id}", response_model=ManagementPlanningResponse)
        async def get_planning(
            planning_id: UUID,
            app: ManagementPlanningApplication = Depends(app_dependency),
        ):
            plannings = await app.get_by_ids([planning_id])
            if not plannings:
                raise HTTPException(status_code=404, detail="planning not found")
            return plannings[0]

        @self.get("/", response_model=list[ManagementPlanningResponse])
        async def get_plannings(
            ids: list[UUID] | None = Query(default=None),
            app: ManagementPlanningApplication = Depends(app_dependency),
        ):
            ids = ids or []
            return await app.get_by_ids(ids)
