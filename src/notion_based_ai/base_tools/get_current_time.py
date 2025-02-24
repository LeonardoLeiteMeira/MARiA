from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class GetCurrentTimeInput(BaseModel):
    # query: str = Field(description="should be a search query")
    pass


class GetCurrentTime(BaseTool):
    name: str = "get_current_time"
    description: str = "Usefull to filter data. Always use this tool to create the right filters. Returns the current time in the format H:MM AM/PM, Month, Year"
    args_schema: Type[BaseModel] = GetCurrentTimeInput

    def _run(self, *args, **kwargs) -> str:
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%I:%M %p, %B, %Y")
        return current_time
    
    async def _arun(self, *args, **kwargs) -> str:
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%I:%M %p, %B, %Y")
        return current_time