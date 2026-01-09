from pydantic import BaseModel, Field
from typing import Any, Type, cast
from langchain_core.messages.tool import ToolMessage
from pydantic import create_model

from .tool_interface import ToolInterface
from .tool_type_enum import ToolType
from MARiA.graph.state import State
from external.notion import NotionTool


class AskUserData(ToolInterface):
    name: str = "ask_user_data"
    description: str = (
        "Pedir dados ao usuário para que seja possível concluir alguma ação."
    )
    args_schema: Type[BaseModel] = create_model(
        "AskUserDataInput",
        question=(
            str,
            Field(
                ...,
                description="Pergunta em linguagem natural e clara sobre dados necessários para conluir uma ação. A pergunta será enviada diretamente para o usuário via Whatsapp. Lembre-se que o usuário não tem dados técnicos.",
            ),
        ),
    )
    tool_type: ToolType = ToolType.AGENT_REDIRECT

    def _run(self, name: str, *args: Any, **kwargs: Any) -> ToolMessage:
        return cast(ToolMessage, None)

    @classmethod
    async def instantiate_tool(
        cls, state: State, notion_tool: NotionTool | None
    ) -> "AskUserData":
        return AskUserData()
