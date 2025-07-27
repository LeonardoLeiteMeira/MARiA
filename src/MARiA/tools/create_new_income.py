from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from external.notion import NotionTool, NotionUserData
from external.notion.enum import UserDataTypes
from pydantic import create_model, Field
from MARiA.tools.tool_interface import ToolInterface
from pydantic import PrivateAttr

class CreateNewIncome(ToolInterface):
    name: str = "criar_nova_transacao_de_entrada"
    description: str = "Cria uma nova transação de entrada com os dados fornecidos - se o usuário não fornecer nenhum parâmetro, é necessário perguntar."
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
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'CreateNewIncome':
        cards = await notion_user_data.get_user_cards()
        months = await notion_user_data.get_user_months()

        from enum import Enum
        CardEnum = Enum(
            "CardEnum",
            {card["Name"].upper(): card["Name"] for card in cards['data']},
        )
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months['data']},
        )

        InputModel = create_model(
            "CreateNewIncomeInputDynamic",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            amount=(float, Field(..., description="Valor da transação")),
            date=(str, Field(..., description="Data ISO da transação")),
            hasPaid=(bool, Field(..., description="Se a transação foi paga ou não. O default é True")),
            card_or_account=(
                CardEnum,
                Field(..., description="Cartão ou conta utilizada na entrada"),
            ),
            month=(
                MonthsEnum,
                Field(..., description="Mês ou gestão em que ocorreu a entrada"),
            ),
        )

        tool = CreateNewIncome(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            amount = parms['args']['amount']
            date = parms['args']['date']
            card_or_account = parms['args']['card_or_account']
            month = parms['args']['month']
            hasPaid = parms['args']['hasPaid'] if 'hasPaid' in parms['args'] else True

            month_id = await self.__notion_user_data.get_data_id(UserDataTypes.MONTHS, month)
            card_id = await self.__notion_user_data.get_data_id(UserDataTypes.CARDS_AND_ACCOUNTS, card_or_account)

            await self.__notion_tool.create_income(
                name = name,
                month_id = month_id,
                amount = amount,
                date = date,
                card_id = card_id,
                hasPaid = hasPaid,
            )
            return ToolMessage(
                content="Criado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
