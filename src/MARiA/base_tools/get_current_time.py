from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class GetCurrentTimeInput(BaseModel):
    pass


class GetCurrentTime(BaseTool):
    name: str = "get_current_time"
    description: str = "Usefull to filter data. Always use this tool to create the right filters. Returns the current time in the format H:MM AM/PM, Month, Year"
    args_schema: Type[BaseModel] = GetCurrentTimeInput

    def _run(self, *args, **kwargs) -> str:
        from datetime import datetime
        try:
            now = datetime.now()
            current_time = now.strftime("%I:%M %p, %B %d, %Y")
            return current_time
        except Exception as e:
            return str(e)
