from typing import Any, Type, cast

from langchain_core.messages.tool import ToolMessage
from pydantic import BaseModel, Field, create_model

from external.notion import NotionTool

from .tool_interface import ToolInterface
from .tool_type_enum import ToolType
from MARiA.graph.state import State


class RequestSaveMemory(ToolInterface):
    name: str = "solicitar_salvar_memoria"
    description: str = (
        "Sinaliza que uma informação financeira estável ou útil no longo prazo "
        "deve ser avaliada para memória. Use apenas uma descrição completa em "
        "linguagem natural."
    )
    args_schema: Type[BaseModel] = create_model(
        "RequestSaveMemoryInput",
        description=(
            str,
            Field(
                ...,
                description=(
                    "Descrição completa, em linguagem natural, da informação que "
                    "pode virar memória de longo prazo."
                ),
            ),
        ),
    )
    tool_type: ToolType = ToolType.MEMORY_SIGNAL

    def _run(self, *args: Any, **kwargs: Any) -> ToolMessage:
        return cast(ToolMessage, None)

    @classmethod
    async def instantiate_tool(
        cls, state: State, notion_tool: NotionTool | None
    ) -> "RequestSaveMemory":
        return RequestSaveMemory()
