from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from application import CategoryApplication
from .request_models.category import CategoryRequest
from .response_models.category import CategoryResponse, MacroCategoryResponse


class CategoryController(APIRouter):
    """Controller grouping category and macro category endpoints."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], CategoryApplication]):
        super().__init__(dependencies=[Depends(jwt_dependency)])

        # --- Category endpoints -----------------------------------------
        @self.post("/categories", response_model=CategoryResponse)
        async def create_category(
            request: Request,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
            user = request.state.user
            data.user_id = str(user.id)
            return await app.create_category(data)

        @self.put("/categories/{category_id}", response_model=CategoryResponse)
        async def update_category(
            request: Request,
            category_id: UUID,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
            user = request.state.user
            data.user_id = str(user.id)
            return await app.update_category(category_id, data)

        @self.delete("/categories/{category_id}")
        async def delete_category(
            category_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            await app.delete_category(category_id)
            return {"detail": "deleted"}

        @self.get("/categories/user/{user_id}", response_model=list[CategoryResponse])
        async def get_categories_by_user(
            user_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            return await app.get_categories_by_user(user_id)

        @self.get("/categories/{category_id}", response_model=CategoryResponse)
        async def get_category(
            category_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            categories = await app.get_categories_by_ids([category_id])
            if not categories:
                raise HTTPException(status_code=404, detail="category not found")
            return categories[0]

        @self.get("/categories", response_model=list[CategoryResponse])
        async def get_categories(
            ids: list[UUID] | None = Query(default=None),
            app: CategoryApplication = Depends(app_dependency),
        ):
            ids = ids or []
            return await app.get_categories_by_ids(ids)

        # --- Macro category endpoints -----------------------------------
        @self.post("/macro-categories", response_model=MacroCategoryResponse)
        async def create_macro_category(
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
            return await app.create_macro_category(data)

        @self.put("/macro-categories/{macro_id}", response_model=MacroCategoryResponse)
        async def update_macro_category(
            macro_id: UUID,
            data: CategoryRequest,
            app: CategoryApplication = Depends(app_dependency),
        ):
            return await app.update_macro_category(macro_id, data)

        @self.delete("/macro-categories/{macro_id}")
        async def delete_macro_category(
            macro_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            await app.delete_macro_category(macro_id)
            return {"detail": "deleted"}

        @self.get("/macro-categories/user/{user_id}", response_model=list[MacroCategoryResponse])
        async def get_macro_by_user(
            user_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            return await app.get_macro_categories_by_user(user_id)

        @self.get("/macro-categories/{macro_id}", response_model=MacroCategoryResponse)
        async def get_macro_category(
            macro_id: UUID,
            app: CategoryApplication = Depends(app_dependency),
        ):
            macros = await app.get_macro_categories_by_ids([macro_id])
            if not macros:
                raise HTTPException(status_code=404, detail="macro category not found")
            return macros[0]

        @self.get("/macro-categories", response_model=list[MacroCategoryResponse])
        async def get_macro_categories(
            ids: list[UUID] | None = Query(default=None),
            app: CategoryApplication = Depends(app_dependency),
        ):
            ids = ids or []
            return await app.get_macro_categories_by_ids(ids)
