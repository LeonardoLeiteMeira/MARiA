from uuid import UUID
from typing import TYPE_CHECKING, List

from domain import CategoryDomain, MacroCategoryDomain
from repository import CategoryModel, MacroCategoryModel

if TYPE_CHECKING:
    from controllers.request_models.category import CategoryRequest


class CategoryApplication:
    """Application layer that orchestrates categories and macro categories."""

    def __init__(
        self,
        category_domain: CategoryDomain,
        macro_category_domain: MacroCategoryDomain,
    ):
        self._category_domain = category_domain
        self._macro_category_domain = macro_category_domain

    # Category operations -------------------------------------------------
    async def create_category(
        self, data: List["CategoryRequest"]
    ) -> List[CategoryModel]:
        categories = [
            CategoryModel(user_id=cat.user_id, name=cat.name, icon=cat.icon)
            for cat in data
        ]
        return await self._category_domain.create(categories)

    async def update_category(
        self, category_id: UUID, data: "CategoryRequest"
    ) -> CategoryModel:
        category = CategoryModel(
            id=category_id, user_id=data.user_id, name=data.name, icon=data.icon
        )
        return await self._category_domain.update(category)

    async def delete_category(self, category_id: UUID, user_id: UUID) -> None:
        # delegate deletion with user filter to domain layer
        await self._category_domain.delete(category_id, user_id)

    async def get_categories_by_ids(
        self, category_ids: list[UUID]
    ) -> list[CategoryModel]:
        return await self._category_domain.get_by_ids(category_ids)

    async def get_categories_by_user(self, user_id: UUID) -> list[CategoryModel]:
        return await self._category_domain.get_by_user_id(user_id)

    # Macro category operations ------------------------------------------
    async def create_macro_category(
        self, list_data: List["CategoryRequest"]
    ) -> List[MacroCategoryModel]:
        macro_list = [MacroCategoryModel(**(data.model_dump())) for data in list_data]
        return await self._macro_category_domain.create(macro_list)

    async def update_macro_category(
        self, macro_id: UUID, data: "CategoryRequest"
    ) -> MacroCategoryModel:
        macro = MacroCategoryModel(
            id=macro_id, user_id=data.user_id, name=data.name, icon=data.icon
        )
        return await self._macro_category_domain.update(macro)

    async def delete_macro_category(self, macro_id: UUID, user_id: UUID) -> None:
        await self._macro_category_domain.delete(macro_id, user_id)

    async def get_macro_categories_by_ids(
        self, macro_ids: list[UUID]
    ) -> list[MacroCategoryModel]:
        return await self._macro_category_domain.get_by_ids(macro_ids)

    async def get_macro_categories_by_user(
        self, user_id: UUID
    ) -> list[MacroCategoryModel]:
        return await self._macro_category_domain.get_by_user_id(user_id)
