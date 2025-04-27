from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_types import NotionDatabaseEnum

class GetTransactionTypesInput(BaseModel):
    cursor: str | None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")


class GetTransactionTypes(BaseTool):
    name: str = "buscar_tipos_de_transacao"
    description: str = "Listar todos os possiveis tipos para uma transação. "
    args_schema: Type[BaseModel] = GetTransactionTypesInput

    def _run(self, cursor: str = None, *args, **kwargs) -> list[dict]:
        pass
        
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ..notion_repository import notion_access
        try:
            cursor = parms['args']['cursor']
            transaction_types = notion_access.get_simple_data(NotionDatabaseEnum.TYPES, cursor)
            return ToolMessage(
                content=transaction_types,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("GetTransactionTypes - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
