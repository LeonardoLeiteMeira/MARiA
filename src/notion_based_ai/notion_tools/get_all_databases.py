from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GeAllDatabasesInput(BaseModel):
    pass


class GeAllDatabases(BaseTool):
    name: str = "buscar_todos_databases"
    description: str = "Listar todas as possíveis bases de dados"
    args_schema: Type[BaseModel] = GeAllDatabasesInput

    def _run(self, *args, **kwargs) -> list[str]:
        try:
            return [x.value for x in Database]
        except Exception as e:
            return str(e)
