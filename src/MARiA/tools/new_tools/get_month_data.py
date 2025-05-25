from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_repository import NotionUserData, notion_user_data, notion_access
from MARiA.notion_repository.notion_user_data import UserDataTypes
from pydantic import create_model, Field
from MARiA.tools.new_tools.tool_interface import ToolInterface
from pydantic import PrivateAttr
from MARiA.notion_types import TransactionType

class GetMonthData(BaseTool, ToolInterface):
    name: str = "buscar_dados_mes"
    description: str = "Busca todos os dados de um mês especifico. Inclui os totais planejado, gasto, receitas, valores previstos e concluidos e mais."
    args_schema: Type[BaseModel] = None
    _notion_user_data: NotionUserData = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, **data):
        super().__init__(**data)
        self._notion_user_data = notion_user_data

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData) -> 'GetMonthData':
        user_data = await notion_user_data.get_user_base_data()

        from enum import Enum
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in user_data.months['data']},
        )

        InputModel = create_model(
            "GetMonthInputData",
            month=(
                MonthsEnum|None,
                Field(..., description="Filtrar o Mês"),
            )
        )

        tool = GetMonthData(notion_user_data=notion_user_data)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            month = parms['args']['month']

            month_id = await self._notion_user_data.get_data_id(UserDataTypes.MONTHS, month)

            month = notion_access.get_page_by_id(month_id, ['Planejamentos', 'This (Não alterar)', 'Transações'])

            return ToolMessage(
                content=month,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
