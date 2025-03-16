from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetDataStructureInput(BaseModel):
    database_name: str = Field(description="Nome da base dade dados para busca a estrutura")


class GetDataStructure(BaseTool):
    name: str = "buscar_estrutura_base_de_dados"
    description: str = "Use this tool to understand the structures before choosing another tool. Useful for obtaining property IDs and understanding the data structure of a database. Property IDs can be used to filter data."
    args_schema: Type[BaseModel] = GetDataStructureInput

    def _run(self, database_name: str, *args, **kwargs) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            valid_databases = [x.value for x in Database]
            if database_name not in valid_databases:
                return ['Este não é um nome valido de base de dados. Verifique a lista de bases de dados validas!']
            return notion_access.get_properties(database_name)
        except Exception as e:
            return str(e)
