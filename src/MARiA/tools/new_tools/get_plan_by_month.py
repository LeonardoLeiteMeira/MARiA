from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import PrivateAttr
from pydantic import create_model, Field

from MARiA.tools.new_tools.tool_interface import ToolInterface
from external import NotionUserData, NotionTool
from external.enum import UserDataTypes

class GetPlanByMonth(BaseTool, ToolInterface):
    name: str = "buscar_planejamento_por_mes"
    description: str = "Busca um planejamento de um mes em especifico."
    args_schema: Type[BaseModel] = None
    __notion_user_data: NotionUserData = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__notion_user_data = notion_user_data
        self.__notion_tool = notion_tool

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'GetPlanByMonth':
        user_data = await notion_user_data.get_user_base_data()

        from enum import Enum
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in user_data.months['data']},
        )

        InputModel = create_model(
            "GetPlanByMonthInput",
            month=(
                MonthsEnum|None,
                Field(..., description="Filtrar o Mês"),
            )
        )

        tool = GetPlanByMonth(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            month = parms['args']['month']

            month_id = await self.__notion_user_data.get_data_id(UserDataTypes.MONTHS, month)

            month_plan = await self.__notion_tool.get_plan_by_month(month_id)

            return ToolMessage(
                content=month_plan,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
