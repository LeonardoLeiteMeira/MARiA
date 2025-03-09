from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetUserCardsInput(BaseModel):
    pass


class GetUserCards(BaseTool):
    name: str = "buscar_contas_e_cartoes"
    description: str = "Listar todas as possíveis contas e cartões que podem ser usadas para uma transação"
    args_schema: Type[BaseModel] = GetUserCardsInput

    def _run(self, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_transactio_repository
        return notion_transactio_repository.get_simple_data(Database.CARDS)