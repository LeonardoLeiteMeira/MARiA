from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from external import NotionTool, NotionUserData
from .tool_interface import ToolInterface

class CreateCard(BaseTool, ToolInterface):
    name: str = "criar_nova_conta_ou_cartao"
    description: str = "Cria uma nova conta ou cartão para registrar entras e saidas"
    args_schema: Type[BaseModel] = None
    __notion_user_data: NotionUserData = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__notion_user_data = notion_user_data
        self.__notion_tool = notion_tool

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'CreateCard':
        InputModel = create_model(
            "CreateCardInput",
            name=(str, Field(..., description="Nome do cartao")),
            initial_balance=(float, Field(..., description="Saldo inicial da conta ou cartão")),
        )

        tool = CreateCard(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            initial_balance = parms['args']['initial_balance']

            await self.__notion_tool.create_card(name, initial_balance)

            return ToolMessage(
                content="Criado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
