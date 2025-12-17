from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from .tool_interface import ToolInterface
from MARiA.graph.state import State

class ReadUserBaseData(ToolInterface):
    name: str = "ler_dados_base_do_usuario"
    description: str = "Acesso a dados como, categorias, meses, cartoes, constas e mais. As informações cadastradas pelo usuário são acessíveis por aqui."
    args_schema: Type[BaseModel] = None
    __state: State = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__state = state
        self.__notion_tool = notion_tool

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'ReadUserBaseData':
        InputModel = create_model(
            "ReadUserBaseDataInput",
            user_datas=(list[UserDataTypes], Field(..., description="Dados a serem lidos")),
        )

        tool = ReadUserBaseData(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            user_datas = parms['args']['user_datas']

            resp = []
            for user_data in user_datas:
                key = user_data.value if isinstance(user_data, UserDataTypes) else user_data
                resp.append(self.__state.get(key))

            return ToolMessage(
                content=str(resp),
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
