from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionUserData, NotionTool
from external.notion.enum import UserDataTypes


class CreateNewOutTransactionV2(ToolInterface):
    name: str = "criar_nova_transacao_de_saida"
    description: str = "Cria uma nova transação de saída com os dados fornecidos. Apenas categoria e macro-categoria sao opcionais!"
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
        cards = await notion_user_data.get_user_cards()
        categories = await notion_user_data.get_user_categories()
        macroCategories = await notion_user_data.get_user_macro_categories()
        months = await notion_user_data.get_user_months()

        from enum import Enum
        CardEnum = Enum(
            "CardEnum",
            {card["Name"].upper(): card["Name"] for card in cards['data']},
        )
        CategoriesEnum = Enum(
            "CategoryEnum",
            {category["Name"].upper(): category["Name"] for category in categories['data']},
        )
        MacroCategoriesEnum = Enum(
            "macroCategoryEnum",
            {macro["Name"].upper(): macro["Name"] for macro in macroCategories['data']},
        )
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months['data']},
        )

        InputModel = create_model(
            "CreateNewOutTransactionInputDynamic",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            amount=(float, Field(..., description="Valor da transação")),
            date=(str, Field(..., description="Data ISO da transação. Use a data correta. Se o usuario nao fornecer use a de hoje!")),
            hasPaid=(bool, Field(..., description="Se a transação foi paga ou não. Se o usuário não informar, deve ser True!")),
            card_or_account=(
                CardEnum,
                Field(..., description="Cartão ou conta utilizada na saída"),
            ),
            category=(
                Optional[CategoriesEnum],
                Field(None, description="Categoria que classifica essa saída. Opcional."),
            ),
            macro_category=(
                Optional[MacroCategoriesEnum],
                Field(None, description="Categoria macro da saída. Opcional."),
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
            args_data = parms['args']
            name = args_data['name']
            amount = args_data['amount']
            date = args_data['date']
            card_or_account = args_data['card_or_account']
            category = args_data.get('category')
            macro_category = args_data.get('macro_category')
            month = args_data['month']
            hasPaid = args_data['hasPaid'] if 'hasPaid' in args_data else True

            month_id = await self.__notion_user_data.get_data_id(UserDataTypes.MONTHS, month)
            card_id = await self.__notion_user_data.get_data_id(UserDataTypes.CARDS_AND_ACCOUNTS, card_or_account)
            category_id = await self.__notion_user_data.get_data_id(UserDataTypes.CATEGORIES, category) if category else None
            macro_category_id = await self.__notion_user_data.get_data_id(UserDataTypes.MACRO_CATEGORIES, macro_category) if macro_category else None

            await self.__notion_tool.create_expense(
                name,
                month_id,
                amount,
                date,
                card_id,
                category_id,
                macro_category_id,
                hasPaid
            )
            return ToolMessage(
                content="Criado com sucesso! Retorne para o usuário para ele saber exatamente o que foi criado!",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
        
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
