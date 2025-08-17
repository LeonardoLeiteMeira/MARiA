from uuid import UUID

from repository import MacroCategoryRepository, MacroCategoryModel


class MacroCategoryDomain:
    """Domain layer for macro category operations."""

    def __init__(self, repo: MacroCategoryRepository):
        self._repo = repo

    async def create(self, macro: MacroCategoryModel) -> MacroCategoryModel:
        await self._repo.create(macro)
        return macro

    async def update(self, macro: MacroCategoryModel) -> MacroCategoryModel:
        await self._repo.update(macro)
        return macro

    async def delete(self, macro_id: UUID) -> None:
        macro = MacroCategoryModel(id=macro_id)
        await self._repo.delete(macro)

    async def get_by_ids(self, macro_ids: list[UUID]) -> list[MacroCategoryModel]:
        return await self._repo.get_by_ids(macro_ids)

    async def get_by_user_id(self, user_id: UUID) -> list[MacroCategoryModel]:
        return await self._repo.get_by_user_id(user_id)
