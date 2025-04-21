from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_types import NotionDatabaseEnum

class GetTransactionsCategoriesInput(BaseModel):
    cursor: str|None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")


class GetTransactionsCategories(BaseTool):
    name: str = "buscar_categorias_de_transacoes"
    description: str = "Listar todas as possíveis categorias para uma transação"
    args_schema: Type[BaseModel] = GetTransactionsCategoriesInput

    def _run(self, cursor:str = None, *args, **kwargs) -> list[dict]:
        pass
    
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ..notion_repository import notion_access
        try:
            cursor = parms['args']['cursor']
            transactions_categories = notion_access.get_simple_data(NotionDatabaseEnum.CATEGORIES, cursor)
            return ToolMessage(
                content=transactions_categories,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("GetTransactionsCategories - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução {e}",
                tool_call_id=parms['id'],
            )
