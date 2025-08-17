from uuid import UUID

from repository import CategoryRepository, CategoryModel


class CategoryDomain:
    """Domain layer for category operations."""

    def __init__(self, repo: CategoryRepository):
        self._repo = repo

    async def create(self, category: CategoryModel) -> CategoryModel:
        await self._repo.create(category)
        return category

    async def update(self, category: CategoryModel) -> CategoryModel:
        await self._repo.update(category)
        return category

    async def delete(self, category_id: UUID) -> None:
        category = CategoryModel(id=category_id)
        await self._repo.delete(category)

    async def get_by_ids(self, category_ids: list[UUID]) -> list[CategoryModel]:
        return await self._repo.get_by_ids(category_ids)

    async def get_by_user_id(self, user_id: UUID) -> list[CategoryModel]:
        return await self._repo.get_by_user_id(user_id)
