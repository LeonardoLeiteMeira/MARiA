from enum import Enum
from pydantic import BaseModel, Field
from typing import Type
from langchain_core.messages.tool import ToolMessage
from pydantic import create_model, Field

from .tool_interface import ToolInterface
from .tool_type_enum import ToolType


class AskUserData(ToolInterface):
    name: str = "ask_user_data"
    description: str = "Pedir dados ao usuário para que seja possível concluir alguma ação."
    args_schema: Type[BaseModel] = create_model(
        "AskUserDataInput",
        question=(str, Field(..., description="Pergunta em linguagem natural e clara sobre dados necessários para conluir uma ação. A pergunta será enviada diretamente para o usuário via Whatsapp. Lembre-se que o usuário não tem dados técnicos."))
    )
    tool_type: ToolType = ToolType.AGENT_REDIRECT

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, notion_user_data: None, notion_tool: None) -> 'AskUserData':
        return AskUserData()