from pydantic import BaseModel, Field
from typing import Any, Type, cast
from langchain_core.messages.tool import ToolMessage
from pydantic import create_model, Field

from .tool_interface import ToolInterface
from .tool_type_enum import ToolType
from MARiA.graph.state import State
from external.notion import NotionTool


class GoToSupervisor(ToolInterface):
    name: str = "go_to_supervisor"
    description: str = "Util quando a tarefa é conlcuida, o assunto muda, o usuário pede que determinada ação seja cancelada, ou quando não se tem a capacidade de executar uma determinada tarefa - Então deve ser redirecionadao para o agente supervisor."
    args_schema: Type[BaseModel] = create_model(
        "GoToSupervisorInput",
        justification=(str, Field(..., description="Justificativa do motivo pelo qual você está escolhendo ir para o supervisor. Frase curta e direta."))
    )
    tool_type: ToolType = ToolType.AGENT_REDIRECT

    def _run(self, name: str, *args: Any, **kwargs: Any) -> ToolMessage:
        return cast(ToolMessage, None)

    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool | None) -> 'GoToSupervisor':
        return GoToSupervisor()
