from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio
# from notion_based_ai.notion_types import Database

class GetMonthsInput(BaseModel):
    year: int = Field(description="The year of the months to be listed")
    property_ids: list[str] = Field(
        description="""
            A list of property IDs to be returned.
By default, the ID of the 'title' is already included, but if you want additional properties, you need to read the structure and specify the IDs here.
        """)


class GetMonths(BaseTool):
    name: str = "get_months"
    description: str = "List months created by user to group transactions by year. It possible to specify more properties to be returned."
    args_schema: Type[BaseModel] = GetMonthsInput

    def _run(self, year:int, property_ids: list[str] = [],*args, **kwargs) -> list[dict]:
        "List months created by user to group transactions by year"
        return asyncio.run(self._arun(year, property_ids))

    async def _arun(
        self,
        year:int,
        property_ids: list[str] = [],
        *args, **kwargs
    ) -> list[dict]:
        "List months created by user to group transactions by year"
        from ..notion_repository import notion_transactio_repository
        return notion_transactio_repository.get_months_by_year(year, property_ids)