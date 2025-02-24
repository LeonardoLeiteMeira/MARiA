from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class GetDataStructureInput(BaseModel):
    database_name: str = Field(description="Name of the database to get the data structure from")


class GetDataStructure(BaseTool):
    name: str = "get_data_sctructure"
    description: str = "Use this tool to understand the structures before choose another tool. Usefull to get properties IDs and undestand the data structure of a database. Properties IDs can be used to filter data."
    args_schema: Type[BaseModel] = GetDataStructureInput

    def _run(self, database_name: str, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun(database_name))

    async def _arun(
        self,
        database: str,
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_transactio_repository
        valid_databases = [x.value for x in Database]
        if database not in valid_databases:
            return ['This is not a valid database name. Check the list of valid databases!']
        return notion_transactio_repository.get_properties(database)