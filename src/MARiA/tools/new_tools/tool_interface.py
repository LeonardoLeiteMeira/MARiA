from abc import ABC, abstractmethod

from domain.notion_tool_domain import NotionToolDomain
from domain import NotionUserDataDomain

class ToolInterface(ABC):
    @classmethod
    @abstractmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserDataDomain, notion_tool: NotionToolDomain):
        pass