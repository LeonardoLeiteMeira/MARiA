from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_repository import NotionUserData, notion_user_data, notion_access
from MARiA.notion_repository.notion_user_data import UserDataTypes
from pydantic import create_model, Field
from MARiA.tools.new_tools.tool_interface import ToolInterface
from pydantic import PrivateAttr

class CreateNewMonth(BaseTool, ToolInterface):
    name: str = "criar_novo_mes"
    description: str = "Cria um novo mes para realizar a gestão financeira."
    args_schema: Type[BaseModel] = None
    _notion_user_data: NotionUserData = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, **data):
        super().__init__(**data)
        self._notion_user_data = notion_user_data

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData) -> 'CreateNewMonth':

        InputModel = create_model(
            "CreateNewMonthInput",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            start_date=(str, Field(..., description="Data referencia de inicio para a gestão do mes. Formato ISO!")),
            finish_date=(str, Field(..., description="Data referencia de final para a gestão do mes. Formato ISO!")),
        )

        tool = CreateNewMonth()
        tool._notion_user_data=notion_user_data
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            start_date = parms['args']['start_date']
            finish_date = parms['args']['finish_date']

            notion_access.create_month(
                name,
                start_date,
                finish_date
            )

            return ToolMessage(
                content="Criado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
