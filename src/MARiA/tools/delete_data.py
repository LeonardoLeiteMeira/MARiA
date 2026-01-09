from typing import Any, Optional, Type, cast
from uuid import UUID

from langchain_core.messages.tool import ToolCall, ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field, PrivateAttr, create_model

from external.notion import NotionTool
from MARiA.graph.state import State

from .tool_interface import ToolInterface


class DeleteData(ToolInterface):
    name: str = "deletar_dados_solicitado"
    description: str = "Apaga qualquer informação solicitada, basta passar o Id corretamente. Pode ser utilizada para atualizar também, apagando o registro anterior e criando um novo atualizado."
    args_schema: Type[BaseModel] | None = None
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data: Any) -> None:
        super().__init__(**data)
        self.__notion_tool = notion_tool

    def _run(self, *args: object, **kwargs: object) -> ToolMessage | None:
        return None

    @classmethod
    async def instantiate_tool(
        cls, state: State, notion_tool: NotionTool
    ) -> "DeleteData":
        InputModel = create_model(
            "DeleteDataInput",
            register_id=(
                str,
                Field(..., description="Id da pagina a ser deletada. Deve ser o UUID"),
            ),
        )

        tool = DeleteData(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(
        self,
        input: str | dict[str, Any] | ToolCall,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ToolMessage:
        try:
            input_dict = cast(dict[str, Any], input)
            register_id = input_dict["args"]["register_id"]

            if not self.__is_uuid(register_id):
                return ToolMessage(
                    content="It's necessary to use a valid UUID",
                    tool_call_id=input_dict["id"],
                )

            await self.__notion_tool.delete_data(register_id)

            return ToolMessage(
                content="Apagado com sucesso",
                tool_call_id=input_dict["id"],
            )
        except Exception as e:
            return self.handle_tool_exception(e, input_dict["id"])

    def __is_uuid(self, value: str) -> bool:
        try:
            UUID(value)
            return True
        except (TypeError, ValueError):
            return False
