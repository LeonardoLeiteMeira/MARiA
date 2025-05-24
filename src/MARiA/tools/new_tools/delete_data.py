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

class DeleteData(BaseTool, ToolInterface):
    name: str = "deletar_dados_solicitado"
    description: str = "Apaga qualquer informação solicitada, basta passar o Id corretamente. Pode ser utilizada para atualizar também, apagando o registro anterior e criando um novo atualizado."
    args_schema: Type[BaseModel] = None
    _notion_user_data: NotionUserData = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, **data):
        super().__init__(**data)
        self._notion_user_data = notion_user_data

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData) -> 'DeleteData':
        InputModel = create_model(
            "DeleteDataInput",
            register_id=(str, Field(..., description="Id da pagina a ser deletada")),
        )

        tool = DeleteData(notion_user_data=notion_user_data)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ...notion_repository import notion_access
        try:
            register_id = parms['args']['register_id']

            notion_access.delete_page(register_id)

            return ToolMessage(
                content="Apagado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
