from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Any, Optional, Type, cast
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from pydantic import PrivateAttr
from pydantic import create_model, Field

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type

class GetCardsWithBalance(ToolInterface):
    name: str = "buscar_cartoes_e_contas_com_saldo"
    description: str = "Buscar a lista de cartoes e contas com o respectivo saldo."
    args_schema: Type[BaseModel] | None = None
    __state: State = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data: Any) -> None:
        super().__init__(**data)
        self.__state = state
        self.__notion_tool = notion_tool

    def _run(self, *args: object, **kwargs: object) -> ToolMessage | None:
        return None


    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'GetCardsWithBalance':
        tool = GetCardsWithBalance(state=state, notion_tool=notion_tool)
        return tool

    async def ainvoke(
        self,
        input: str | dict[str, Any] | ToolCall,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ToolMessage:
        try:
            accounts = await self.__notion_tool.get_accounts_with_balance()

            return ToolMessage(
                content=cast(str, accounts),
                tool_call_id=cast(dict[str, Any], input)['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, cast(dict[str, Any], input)['id'])
