from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_repository import NotionUserData
from MARiA.notion_types import NotionDatabaseEnum
from pydantic import create_model, Field
from .tool_interface import ToolInterface
from pydantic import PrivateAttr

class CreateCard(BaseTool, ToolInterface):
    name: str = "criar_nova_conta_ou_cartao"
    description: str = "Cria uma nova conta ou cartão para registrar entras e saidas"
    args_schema: Type[BaseModel] = None
    _notion_user_data: NotionUserData = PrivateAttr()

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData) -> 'CreateCard':
        InputModel = create_model(
            "CreateCardInput",
            name=(str, Field(..., description="Nome do cartao")),
            initial_balance=(float, Field(..., description="Saldo inicial da conta ou cartão")),
        )

        tool = CreateCard(notion_user_data=notion_user_data)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ...notion_repository import notion_access
        try:
            name = parms['args']['name']
            initial_balance = parms['args']['initial_balance']

            notion_access.create_card(name, initial_balance)

            return ToolMessage(
                content="Criado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
