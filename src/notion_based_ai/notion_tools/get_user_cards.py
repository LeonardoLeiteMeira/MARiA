from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetUserCardsInput(BaseModel):
    cursor: str|None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")


class GetUserCards(BaseTool):
    name: str = "buscar_contas_e_cartoes"
    description: str = "Listar todas as possíveis contas e cartões que podem ser usadas para uma transação"
    args_schema: Type[BaseModel] = GetUserCardsInput

    def _run(self, cursor: str = None, *args, **kwargs) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_simple_data(Database.CARDS, cursor)
        except Exception as e:
            return str(e)
