from pydantic import BaseModel, Field
from typing import Any, Optional, Type, cast
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from external.notion import NotionTool
from .tool_interface import ToolInterface
from MARiA.graph.state import State

class CreateCard(ToolInterface):
    name: str = "criar_nova_conta_ou_cartao"
    description: str = "Cria uma nova conta ou cartão para registrar entras e saidas. Retorna o cartao criado."
    args_schema: Type[BaseModel] | None = None
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data: Any) -> None:
        super().__init__(**data)
        self.__notion_tool = notion_tool

    def _run(self, *args: object, **kwargs: object) -> ToolMessage | None:
        return None

    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'CreateCard':
        InputModel = create_model(
            "CreateCardInput",
            name=(str, Field(..., description="Nome do cartao")),
            initial_balance=(float, Field(default=0, description="Saldo inicial da conta ou cartão. Default 0")),
        )

        tool = CreateCard(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(
        self,
        input: str | dict[str, Any] | ToolCall,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ToolMessage:
        try:
            input_dict = cast(dict[str, Any], input)
            name = input_dict['args']['name']
            initial_balance = input_dict['args'].get('initial_balance', 0)

            new_card = await self.__notion_tool.create_card(name, initial_balance)

            return ToolMessage(
                content=cast(str, new_card),
                tool_call_id=input_dict['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, input_dict['id'])
