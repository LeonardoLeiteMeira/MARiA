from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool
from external import NotionTool, NotionUserData

class ToolInterface(BaseTool, ABC):
    name: str 
    
    @classmethod
    @abstractmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool):
        pass