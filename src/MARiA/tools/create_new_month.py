from pydantic import BaseModel, Field
from typing import Any, Optional, Type, cast
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from MARiA.graph.state import State


class CreateNewMonth(ToolInterface):
    name: str = "criar_novo_mes"
    description: str = (
        "Cria um novo mes para realizar a gestão financeira. Retorna o mes criado."
    )
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
    ) -> "CreateNewMonth":
        InputModel = create_model(
            "CreateNewMonthInput",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            start_date=(
                str,
                Field(
                    ...,
                    description="Data referencia de inicio para a gestão do mes. Formato ISO!",
                ),
            ),
            finish_date=(
                str,
                Field(
                    ...,
                    description="Data referencia de final para a gestão do mes. Formato ISO!",
                ),
            ),
        )

        tool = CreateNewMonth(state=state, notion_tool=notion_tool)
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
            name = input_dict["args"]["name"]
            start_date = input_dict["args"]["start_date"]
            finish_date = input_dict["args"]["finish_date"]

            new_month = await self.__notion_tool.create_month(
                name, start_date, finish_date
            )

            return ToolMessage(
                content=cast(str, new_month),
                tool_call_id=input_dict["id"],
            )
        except Exception as e:
            return self.handle_tool_exception(e, input_dict["id"])
