from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetTransactionTypesInput(BaseModel):
    cursor: str | None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")


class GetTransactionTypes(BaseTool):
    name: str = "buscar_tipos_de_transacao"
    description: str = "Listar todos os possiveis tipos para uma transação. "
    args_schema: Type[BaseModel] = GetTransactionTypesInput

    def _run(self, cursor: str = None, *args, **kwargs) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_simple_data(Database.TYPES, cursor)
        except Exception as e:
            return str(e)
