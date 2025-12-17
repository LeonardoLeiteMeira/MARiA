from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import PrivateAttr
from pydantic import create_model, Field

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type

class GetPlanByMonth(ToolInterface):
    name: str = "buscar_planejamento_por_mes"
    description: str = "Busca um planejamento de um mes em especifico."
    args_schema: Type[BaseModel] = None
    __state: State = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__state = state
        self.__notion_tool = notion_tool

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'GetPlanByMonth':
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)

        from enum import Enum
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
        )

        InputModel = create_model(
            "GetPlanByMonthInput",
            month=(
                MonthsEnum|None,
                Field(..., description="Filtrar o Mês"),
            )
        )

        tool = GetPlanByMonth(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            month = parms['args']['month']

            month_id = get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)

            month_plan = await self.__notion_tool.get_plan_by_month(month_id)

            return ToolMessage(
                content=month_plan,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
