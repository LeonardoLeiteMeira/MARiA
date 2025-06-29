from abc import ABC, abstractmethod

from external import NotionTool, NotionUserData

class ToolInterface(ABC):
    @classmethod
    @abstractmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool):
        pass