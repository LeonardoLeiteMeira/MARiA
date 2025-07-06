from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.new_tools.tool_interface import ToolInterface
from external import NotionUserData, NotionTool

class CreateNewMonth(ToolInterface):
    name: str = "criar_novo_mes"
    description: str = "Cria um novo mes para realizar a gestão financeira."
    args_schema: Type[BaseModel] = None
    __notion_user_data: NotionUserData = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__notion_user_data = notion_user_data
        self.__notion_tool = notion_tool

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'CreateNewMonth':
        InputModel = create_model(
            "CreateNewMonthInput",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            start_date=(str, Field(..., description="Data referencia de inicio para a gestão do mes. Formato ISO!")),
            finish_date=(str, Field(..., description="Data referencia de final para a gestão do mes. Formato ISO!")),
        )

        tool = CreateNewMonth(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            start_date = parms['args']['start_date']
            finish_date = parms['args']['finish_date']

            await self.__notion_tool.create_month(
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
