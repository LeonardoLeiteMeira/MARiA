from pydantic import BaseModel
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig

from MARiA.notion_types import NotionDatabaseEnum

class GeAllDatabasesInput(BaseModel):
    pass


class GeAllDatabases(BaseTool):
    name: str = "buscar_todos_databases"
    description: str = "Listar todas as possíveis bases de dados"
    args_schema: Type[BaseModel] = GeAllDatabasesInput

    def _run(self, *args, **kwargs) -> ToolMessage:
        return [x.value for x in NotionDatabaseEnum]

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            database_registers = [x.value for x in NotionDatabaseEnum]
            return ToolMessage(
                content=database_registers,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("GeAllDatabases - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução: {e}",
                tool_call_id=parms['id'],
            )
