from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_types import NotionDatabaseEnum

class GetDataStructureInput(BaseModel):
    database_name: str = Field(description="Nome da base dade dados para busca a estrutura")


class GetDataStructure(BaseTool):
    name: str = "buscar_estrutura_base_de_dados"
    description: str = "Use this tool to understand the structures before choosing another tool. Useful for obtaining property IDs and understanding the data structure of a database. Property IDs can be used to filter data."
    args_schema: Type[BaseModel] = GetDataStructureInput

    def _run(self, database_name: str, *args, **kwargs) -> list[dict]:
        pass

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ..notion_repository import notion_access
        try:
            database_name = parms['args']['database_name']
            valid_databases = [x.value for x in NotionDatabaseEnum]
            if database_name not in valid_databases:
                return ToolMessage(
                    content='Este não é um nome valido de base de dados. Verifique a lista de bases de dados validas!',
                    tool_call_id=parms['id'],
                )
            properties = notion_access.get_properties(database_name)
            return ToolMessage(
                content=properties,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("GetDataStructure - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
