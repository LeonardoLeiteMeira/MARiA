from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetTransactionTypesInput(BaseModel):
    # query: str = Field(description="should be a search query")
    pass


class GetTransactionTypes(BaseTool):
    name: str = "get_transaction_types"
    description: str = "List all possible types for transactions"
    args_schema: Type[BaseModel] = GetTransactionTypesInput

    def _run(self, *args, **kwargs) -> list[dict]:
        """Returns a list of all possible types for transactions."""
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        """Returns a list of all possible types for transactions."""
        from ..notion_repository import notion_transactio_repository
        return notion_transactio_repository.get_simple_data(Database.TYPES)