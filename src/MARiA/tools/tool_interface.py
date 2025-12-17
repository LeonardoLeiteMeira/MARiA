from abc import ABC, abstractmethod

from langchain_core.tools import BaseTool
from .tool_type_enum import ToolType
from langchain_core.messages.tool import ToolMessage
import sentry_sdk

from external.notion import NotionTool

from MARiA.graph.state import State


class ToolInterface(BaseTool, ABC):
    name: str
    tool_type: ToolType = ToolType.EXECUTION 
    
    @classmethod
    @abstractmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool | None) -> 'ToolInterface':
        pass

    def handle_tool_exception(self, error: Exception, tool_call_id: str) -> ToolMessage:
        sentry_sdk.capture_exception(error)
        return ToolMessage(
            content=(
                "Ocorreu um erro na execução. Verifique os dados e tente novamente. "
                "Segue o erro para ajudar a entender: "
                f"{error}"
            ),
            tool_call_id=tool_call_id,
        )
