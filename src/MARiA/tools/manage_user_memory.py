from typing import Any, Literal, Optional, Type, Union, cast

from langchain_core.messages.tool import ToolCall, ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field, PrivateAttr

from domain import UserLongTermMemoryDomain
from external.notion import NotionTool

from .tool_interface import ToolInterface
from MARiA.graph.state import State


class ManageUserMemoryInput(BaseModel):
    action: Literal["read", "upsert", "delete"] = Field(
        ...,
        description="Ação a ser realizada na memória do usuário.",
    )
    memory_patch: dict[str, str] | None = Field(
        default=None,
        description="Patch parcial de memória a ser salvo.",
    )
    keys_to_delete: list[str] | None = Field(
        default=None,
        description="Lista de chaves de memória que devem ser removidas.",
    )
    reason: str | None = Field(
        default=None,
        description="Justificativa breve para a ação.",
    )


class ManageUserMemory(ToolInterface):
    name: str = "gerenciar_memoria_usuario"
    description: str = (
        "Lê, atualiza ou remove memórias de longo prazo do usuário."
    )
    args_schema: Type[BaseModel] = ManageUserMemoryInput
    __state: State = PrivateAttr()
    __memory_domain: UserLongTermMemoryDomain = PrivateAttr()

    def __init__(
        self,
        state: State,
        memory_domain: UserLongTermMemoryDomain,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self.__state = state
        self.__memory_domain = memory_domain

    def _run(self, *args: Any, **kwargs: Any) -> ToolMessage:
        return cast(ToolMessage, None)

    @classmethod
    async def instantiate_tool(
        cls, state: State, notion_tool: NotionTool | None
    ) -> "ManageUserMemory":
        raise ValueError(
            "ManageUserMemory must be instantiated directly with a memory domain."
        )

    async def ainvoke(
        self,
        input: Union[str, dict[str, Any], ToolCall],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ToolMessage:
        input_dict = cast(dict[str, Any], input)
        tool_call_id = str(input_dict.get("id", "manage_user_memory"))

        try:
            args_data = cast(dict[str, Any], input_dict["args"])
            action = cast(str, args_data["action"])
            user_id = self.__state["user_id"]

            if action == "read":
                memory = await self.__memory_domain.get_user_memory(user_id)
                return ToolMessage(
                    content="User long-term memory loaded.",
                    artifact=memory,
                    tool_call_id=tool_call_id,
                )

            if action == "upsert":
                memory_patch = cast(dict[str, str] | None, args_data.get("memory_patch"))
                if not memory_patch:
                    return ToolMessage(
                        content="No memory patch provided for upsert.",
                        artifact=self.__state.get("long_term_memory", {}),
                        tool_call_id=tool_call_id,
                    )

                memory = await self.__memory_domain.save_memory_patch(user_id, memory_patch)
                return ToolMessage(
                    content="User long-term memory updated.",
                    artifact=memory,
                    tool_call_id=tool_call_id,
                )

            if action == "delete":
                keys_to_delete = cast(list[str] | None, args_data.get("keys_to_delete"))
                memory = await self.__memory_domain.remove_memory_keys(
                    user_id, keys_to_delete or []
                )
                return ToolMessage(
                    content="User long-term memory updated.",
                    artifact=memory,
                    tool_call_id=tool_call_id,
                )

            return ToolMessage(
                content=f"Unsupported action: {action}",
                artifact=self.__state.get("long_term_memory", {}),
                tool_call_id=tool_call_id,
            )
        except Exception as error:
            return self.handle_tool_exception(error, tool_call_id)
