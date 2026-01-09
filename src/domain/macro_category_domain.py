from uuid import UUID
from typing import List

from repository import MacroCategoryRepository, MacroCategoryModel


class MacroCategoryDomain:
    """Domain layer for macro category operations."""

    def __init__(self, repo: MacroCategoryRepository) -> None:
        self._repo = repo

    async def create(self, macros: List[MacroCategoryModel]) -> List[MacroCategoryModel]:
        return await self._repo.create(macros)

    async def update(self, macro: MacroCategoryModel) -> MacroCategoryModel:
        await self._repo.update(macro)
        return macro

    async def delete(self, macro_id: UUID, user_id: UUID) -> None:
        macro = MacroCategoryModel(id=macro_id, user_id=user_id)
        await self._repo.delete(macro)

    async def get_by_ids(self, macro_ids: list[UUID]) -> list[MacroCategoryModel]:
        return await self._repo.get_by_ids(macro_ids)

    async def get_by_user_id(self, user_id: UUID) -> list[MacroCategoryModel]:
        return await self._repo.get_by_user_id(user_id)
