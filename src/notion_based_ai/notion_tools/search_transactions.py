from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class SearchTransactionsInput(BaseModel):
    cursor: str|None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")


class SearchTransactions(BaseTool):
    name: str = "buscar_transacoes"
    description: str = "Útil quando é necessário buscar palas transações mais recentes"
    args_schema: Type[BaseModel] = SearchTransactionsInput

    def _run(self, cursor: str = None, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun(cursor))

    async def _arun(
        self,
        cursor: str = None,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_transactions(cursor)
        except Exception as e:
            return str(e)
        