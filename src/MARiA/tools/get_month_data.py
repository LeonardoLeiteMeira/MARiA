from typing import Any, Optional, Type, cast

from langchain_core.messages.tool import ToolCall, ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field, PrivateAttr, create_model

from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type
from MARiA.tools.tool_interface import ToolInterface


class GetMonthData(ToolInterface):
    name: str = "buscar_dados_mes"
    description: str = "Busca todos os dados de um mês especifico. Inclui os totais planejado, gasto, receitas, valores previstos e concluidos e mais."
    args_schema: Type[BaseModel] | None = None
    __state: State = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data: Any) -> None:
        super().__init__(**data)
        self.__state = state
        self.__notion_tool = notion_tool

    def _run(self, *args: object, **kwargs: object) -> ToolMessage | None:
        return None

    @classmethod
    async def instantiate_tool(
        cls, state: State, notion_tool: NotionTool
    ) -> "GetMonthData":
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)

        from enum import Enum

        MonthsEnum = Enum(  # type: ignore[misc]
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
        )

        InputModel = create_model(
            "GetMonthInputData",
            month=(
                MonthsEnum | None,
                Field(..., description="Filtrar o Mês"),
            ),
        )

        tool = GetMonthData(state=state, notion_tool=notion_tool)
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
            month = input_dict["args"]["month"]

            month_id = cast(
                str, get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)
            )

            month = await self.__notion_tool.get_month(month_id)

            return ToolMessage(
                content=cast(str, month),
                tool_call_id=input_dict["id"],
            )
        except Exception as e:
            return self.handle_tool_exception(e, input_dict["id"])
