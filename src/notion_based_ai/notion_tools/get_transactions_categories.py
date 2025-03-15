from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetTransactionsCategoriesInput(BaseModel):
    cursor: str|None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")


class GetTransactionsCategories(BaseTool):
    name: str = "buscar_categorias_de_transacoes"
    description: str = "Listar todas as possíveis categorias para uma transação"
    args_schema: Type[BaseModel] = GetTransactionsCategoriesInput

    def _run(self, cursor:str = None, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun(cursor))

    async def _arun(
        self,
        cursor: str = None,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_simple_data(Database.CATEGORIES, cursor)
        except Exception as e:
            return str(e)