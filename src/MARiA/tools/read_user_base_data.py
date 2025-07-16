from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from external.notion import NotionUserData, NotionTool
from external.notion.enum import UserDataTypes
from .tool_interface import ToolInterface

class ReadUserBaseData(ToolInterface):
    name: str = "ler_dados_base_do_usuario"
    description: str = "Acesso a dados como, categorias, meses, cartoes, constas e mais. As informações cadastradas pelo usuário são acessíveis por aqui."
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
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'ReadUserBaseData':
        InputModel = create_model(
            "ReadUserBaseDataInput",
            user_datas=(list[UserDataTypes], Field(..., description="Dados a serem lidos")),
        )

        tool = ReadUserBaseData(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            user_datas = parms['args']['user_datas']
            data = await self.__notion_user_data.get_user_base_data()

            resp = []
            for user_data in user_datas:
                resp.append(getattr(data, user_data))

            return ToolMessage(
                content=str(resp),
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
