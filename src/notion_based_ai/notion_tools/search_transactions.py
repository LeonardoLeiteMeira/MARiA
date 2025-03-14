from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class SearchTransactionsInput(BaseModel):
    pass


class SearchTransactions(BaseTool):
    name: str = "buscar_transacoes"
    description: str = "Útil quando é necessário buscar palas transações mais recentes"
    args_schema: Type[BaseModel] = SearchTransactionsInput

    def _run(self, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_transactions()
        except Exception as e:
            return str(e)
        