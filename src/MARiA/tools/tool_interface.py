from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool
from .tool_type_enum import ToolType
from external.notion import NotionTool, NotionUserData

class ToolInterface(BaseTool, ABC):
    name: str
    tool_type: ToolType = ToolType.EXECUTION 
    
    @classmethod
    @abstractmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData | None, notion_tool: NotionTool | None):
        pass