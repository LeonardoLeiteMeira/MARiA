from collections.abc import Callable
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from application import CategoryApplication
from .request_models.category import CategoryRequest
from .response_models.category import (
    CategoryResponse,
    CategoryListResponse,
    MacroCategoryResponse,
    MacroCategoryListResponse,
)


class CategoryController(APIRouter):
    """Controller grouping category and macro category endpoints."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], CategoryApplication]):
        super().__init__(dependencies=[Depends(jwt_dependency)])

        # --- Category endpoints -----------------------------------------
        @self.post("/categories", response_model=List[CategoryResponse])
        async def create_category(
            request: Request,
            data: List[CategoryRequest],
            app: CategoryApplication = Depends(app_dependency),
        ):
            user_id = request.state.user.id
            for cat in data:
                cat.user_id = user_id
            return await app.create_category(data)

        @self.put("/categories/{category_id}")
        async def update_category(
            category_id: UUID,
            request: Request,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
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
        ):
            # ensure only user's own category is removed
            await app.delete_category(category_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/categories/user", response_model=CategoryListResponse)
        async def get_categories_by_user(
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ):
            # list only categories owned by the authenticated user
            categories = await app.get_categories_by_user(request.state.user.id)
            return CategoryListResponse(data=categories)

        @self.get("/categories/{category_id}", response_model=CategoryResponse)
        async def get_category(
            category_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            categories = await app.get_categories_by_ids([category_id])
            if not categories:
                raise HTTPException(status_code=404, detail="category not found")
            return categories[0]

        @self.get("/categories", response_model=CategoryListResponse)
        async def get_categories(
            ids: list[UUID] | None = Query(default=None),
            app: CategoryApplication = Depends(app_dependency),
        ):
            ids = ids or []
            categories = await app.get_categories_by_ids(ids)
            return CategoryListResponse(data=categories)

        # --- Macro category endpoints -----------------------------------
        @self.post("/macro-categories", response_model=MacroCategoryResponse)
        async def create_macro_category(
            request: Request,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            return await app.create_macro_category(data)

        @self.put("/macro-categories/{macro_id}")
        async def update_macro_category(
            macro_id: UUID,
            request: Request,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            await app.update_macro_category(macro_id, data)
            # signal success with 201 status without serializing model
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/macro-categories/{macro_id}")
        async def delete_macro_category(
            macro_id: UUID,
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ):
            await app.delete_macro_category(macro_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/macro-categories/user", response_model=MacroCategoryListResponse)
        async def get_macro_by_user(
            request: Request,
            app: CategoryApplication = Depends(app_dependency),
        ):
            # fetch macro categories for the authenticated user only
            macros = await app.get_macro_categories_by_user(request.state.user.id)
            return MacroCategoryListResponse(data=macros)

        @self.get("/macro-categories/{macro_id}", response_model=MacroCategoryResponse)
        async def get_macro_category(
            macro_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            macros = await app.get_macro_categories_by_ids([macro_id])
            if not macros:
                raise HTTPException(status_code=404, detail="macro category not found")
            return macros[0]

        @self.get("/macro-categories", response_model=MacroCategoryListResponse)
        async def get_macro_categories(
            ids: list[UUID] | None = Query(default=None),
            app: CategoryApplication = Depends(app_dependency),
        ):
            ids = ids or []
            macros = await app.get_macro_categories_by_ids(ids)
            return MacroCategoryListResponse(data=macros)
