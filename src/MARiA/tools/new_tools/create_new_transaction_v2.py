from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.new_tools.tool_interface import ToolInterface
from external import NotionUserData, NotionTool
from external.enum import UserDataTypes


class CreateNewOutTransactionV2(BaseTool, ToolInterface):
    name: str = "criar_nova_transacao_de_saida"
    description: str = "Cria uma nova transação de saída com os dados fornecidos - se o usuário não fornecer nenhum parâmetro, é necessário perguntar."
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
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'CreateNewOutTransactionV2':
        user_data = await notion_user_data.get_user_base_data()

        from enum import Enum
        CardEnum = Enum(
            "CardEnum",
            {card["Name"].upper(): card["Name"] for card in user_data.cards['data']},
        )
        CategoriesEnum = Enum(
            "CategoryEnum",
            {category["Name"].upper(): category["Name"] for category in user_data.categories['data']},
        )
        MacroCategoriesEnum = Enum(
            "macroCategoryEnum",
            {macro["Name"].upper(): macro["Name"] for macro in user_data.macroCategories['data']},
        )
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in user_data.months['data']},
        )

        InputModel = create_model(
            "CreateNewOutTransactionInputDynamic",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            amount=(float, Field(..., description="Valor da transação")),
            date=(str, Field(..., description="Data ISO da transação")),
            hasPaid=(bool, Field(..., description="Se a transação foi paga ou não. O default é True")),
            card_or_account=(
                CardEnum,
                Field(..., description="Cartão ou conta utilizada na saída"),
            ),
            category=(
                CategoriesEnum,
                Field(..., description="Categoria que classifica essa saída"),
            ),
            macro_category=(
                MacroCategoriesEnum,
                Field(..., description="Categoria macro da saída"),
            ),
            month=(
                MonthsEnum,
                Field(..., description="Mês ou gestão em que ocorreu a transação"),
            ),
        )

        tool = CreateNewOutTransactionV2(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            amount = parms['args']['amount']
            date = parms['args']['date']
            card_or_account = parms['args']['card_or_account']
            category = parms['args']['category']
            macro_category = parms['args']['macro_category']
            month = parms['args']['month']
            hasPaid = parms['args']['hasPaid'] if 'hasPaid' in parms['args'] else True

            month_id = await self.__notion_user_data.get_data_id(UserDataTypes.MONTHS, month)
            card_id = await self.__notion_user_data.get_data_id(UserDataTypes.CARDS_AND_ACCOUNTS, card_or_account)
            category_id = await self.__notion_user_data.get_data_id(UserDataTypes.CATEGORIES, category)
            marco_category_id = await self.__notion_user_data.get_data_id(UserDataTypes.MACRO_CATEGORIES, macro_category)

            await self.__notion_tool.create_expense(
                name,
                month_id,
                amount,
                date,
                card_id,
                category_id,
                marco_category_id,
                hasPaid
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
        
# if __name__ == "__main__":

#     import asyncio

#     async def test():
#         tool = await CreateNewOutTransactionV2.instantiate_tool(notion_user_data)
#         await tool.ainvoke(
#             {
#                 'args': {
#                     'name':'Teste',
#                     'amount':400,
#                     'date':'2025-05-23',
#                     'card_or_account':'NuConta',
#                     'category':'Diversos',
#                     'macro_category':'Não Essencial',
#                     'month':'2025 - Maio',
#                 }
#             },
#             {}
#         )
#     asyncio.run(test())
