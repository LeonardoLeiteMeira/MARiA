from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetTransactionsCategoriesInput(BaseModel):
    pass


class GetTransactionsCategories(BaseTool):
    name: str = "buscar_categorias_de_transacoes"
    description: str = "Listar todas as possíveis categorias para uma transação"
    args_schema: Type[BaseModel] = GetTransactionsCategoriesInput

    def _run(self, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_transactio_repository
        return notion_transactio_repository.get_simple_data(Database.CATEGORIES)