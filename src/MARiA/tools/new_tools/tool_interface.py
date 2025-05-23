from abc import ABC, abstractmethod
from MARiA.notion_repository import NotionUserData

class ToolInterface(ABC):
    @classmethod
    @abstractmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData):
        pass