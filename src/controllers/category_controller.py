from collections.abc import Callable
from uuid import UUID
from typing import List, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from application import CategoryApplication
from .request_models.category import CategoryRequest
from .response_models.category import (
    CategoryResponse,
    MacroCategoryResponse,
    MacroCategoryListResponse,
)


class CategoryController(APIRouter):
    """Controller grouping category and macro category endpoints."""

    def __init__(
        self,
        jwt_dependency: Callable[..., Any],
        app_dependency: Callable[[], CategoryApplication],
    ):
        super().__init__(dependencies=[Depends(jwt_dependency)])

        # --- Category endpoints -----------------------------------------
        @self.post("/categories", response_model=List[CategoryResponse])
        async def create_category(
            request: Request,
            data: List[CategoryRequest],
            app: CategoryApplication = Depends(app_dependency),
        ) -> List[CategoryResponse]:
            user_id = request.state.user.id
            for cat in data:
                cat.user_id = user_id
            return cast(List[CategoryResponse], await app.create_category(data))

        @self.put("/categories/{category_id}")
        async def update_category(
            category_id: UUID,
            request: Request,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ) -> Response:
            # replace user supplied in payload by authenticated user
            data.user_id = request.state.user.id
            await app.update_category(category_id, data)
            # return 201 to acknowledge update without returning body
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/categories/{category_id}")
        async def delete_category(
            category_id: UUID,
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            # ensure only user's own category is removed
            await app.delete_category(category_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/categories/user", response_model=list[CategoryResponse])
        async def get_categories_by_user(
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ) -> list[CategoryResponse]:
            # list only categories owned by the authenticated user
            categories = await app.get_categories_by_user(request.state.user.id)
            return cast(list[CategoryResponse], categories)

        @self.get("/categories/{category_id}", response_model=CategoryResponse)
        async def get_category(
            category_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ) -> CategoryResponse:
            categories = await app.get_categories_by_ids([category_id])
            if not categories:
                raise HTTPException(status_code=404, detail="category not found")
            return cast(CategoryResponse, categories[0])

        @self.get("/categories", response_model=list[CategoryResponse])
        async def get_categories(
            ids: list[UUID] | None = Query(default=None),
            app: CategoryApplication = Depends(app_dependency),
        ) -> list[CategoryResponse]:
            ids = ids or []
            categories = await app.get_categories_by_ids(ids)
            return cast(list[CategoryResponse], categories)

        # --- Macro category endpoints -----------------------------------
        @self.post("/macro-categories", response_model=List[MacroCategoryResponse])
        async def create_macro_category(
            request: Request,
            data: List[CategoryRequest],
            app: CategoryApplication = Depends(app_dependency),
        ) -> List[MacroCategoryResponse]:
            user_id = request.state.user.id
            for cat in data:
                cat.user_id = user_id
            return cast(
                List[MacroCategoryResponse], await app.create_macro_category(data)
            )

        @self.put("/macro-categories/{macro_id}")
        async def update_macro_category(
            macro_id: UUID,
            request: Request,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ) -> Response:
            data.user_id = request.state.user.id
            await app.update_macro_category(macro_id, data)
            # signal success with 201 status without serializing model
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/macro-categories/{macro_id}")
        async def delete_macro_category(
            macro_id: UUID,
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            await app.delete_macro_category(macro_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/macro-categories/user", response_model=list[MacroCategoryResponse])
        async def get_macro_by_user(
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ) -> list[MacroCategoryResponse]:
            # fetch macro categories for the authenticated user only
            macros = await app.get_macro_categories_by_user(request.state.user.id)
            return cast(list[MacroCategoryResponse], macros)

        @self.get("/macro-categories/{macro_id}", response_model=MacroCategoryResponse)
        async def get_macro_category(
            macro_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ) -> MacroCategoryResponse:
            macros = await app.get_macro_categories_by_ids([macro_id])
            if not macros:
                raise HTTPException(status_code=404, detail="macro category not found")
            return cast(MacroCategoryResponse, macros[0])

        @self.get("/macro-categories", response_model=MacroCategoryListResponse)
        async def get_macro_categories(
            ids: list[UUID] | None = Query(default=None),
            app: CategoryApplication = Depends(app_dependency),
        ) -> MacroCategoryListResponse:
            ids = ids or []
            macros = await app.get_macro_categories_by_ids(ids)
            return MacroCategoryListResponse(
                data=cast(list[MacroCategoryResponse], macros)
            )
