from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetTransactionTypesInput(BaseModel):
    pass


class GetTransactionTypes(BaseTool):
    name: str = "buscar_tipos_de_transacao"
    description: str = "Listar todos os possiveis tipos para uma transação"
    args_schema: Type[BaseModel] = GetTransactionTypesInput

    def _run(self, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_simple_data(Database.TYPES)
        except Exception as e:
            return str(e)