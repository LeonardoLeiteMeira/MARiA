from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from external.notion import NotionTool
from .tool_interface import ToolInterface
from MARiA.graph.state import State

class CreateCard(ToolInterface):
    name: str = "criar_nova_conta_ou_cartao"
    description: str = "Cria uma nova conta ou cartão para registrar entras e saidas"
    args_schema: Type[BaseModel] = None
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__notion_tool = notion_tool

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'CreateCard':
        InputModel = create_model(
            "CreateCardInput",
            name=(str, Field(..., description="Nome do cartao")),
            initial_balance=(float, Field(..., description="Saldo inicial da conta ou cartão")),
        )

        tool = CreateCard(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            initial_balance = parms['args']['initial_balance']

            new_card = await self.__notion_tool.create_card(name, initial_balance)

            return ToolMessage(
                content=new_card,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
