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


class DeleteData(ToolInterface):
    name: str = "deletar_dados_solicitado"
    description: str = "Apaga qualquer informação solicitada, basta passar o Id corretamente. Pode ser utilizada para atualizar também, apagando o registro anterior e criando um novo atualizado."
    args_schema: Type[BaseModel] = None
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__notion_tool = notion_tool

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'DeleteData':
        InputModel = create_model(
            "DeleteDataInput",
            register_id=(str, Field(..., description="Id da pagina a ser deletada")),
        )

        tool = DeleteData(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            register_id = parms['args']['register_id']

            await self.__notion_tool.delete_data(register_id)

            return ToolMessage(
                content="Apagado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
