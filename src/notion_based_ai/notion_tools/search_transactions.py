from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class SearchTransactionsInput(BaseModel):
    # query: str = Field(description="should be a search query")
    pass


class SearchTransactions(BaseTool):
    name: str = "search_transactions"
    description: str = "Usufull when tou need to search for the latest transactions"
    args_schema: Type[BaseModel] = SearchTransactionsInput

    def _run(self, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        """Returns a list of more recent transactions."""
        from ..notion_repository import notion_transactio_repository
        return notion_transactio_repository.get_transactions()
        