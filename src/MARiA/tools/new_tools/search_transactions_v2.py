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

class SearchTransactionV2(BaseTool, ToolInterface):
    name: str = "buscar_transacoes_com_parametros"
    description: str = "Fazer busca de transacoes com base nas informacoes que o usuario passar. Use apenas as informações que o usuário passar, o que ele não passar deixe como None"
    args_schema: Type[BaseModel] = None
    _notion_user_data: NotionUserData = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, **data):
        super().__init__(**data)
        self._notion_user_data = notion_user_data

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData) -> 'SearchTransactionV2':
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
            name=(str | None, Field(..., description="Filtrar por nome")),
            hasPaid=(bool | None, Field(..., description="Filtar transações pagas ou pendentes. True são as já pagas, False são as pendentes.")),
            card_account_enter=(
                CardEnum|None,
                Field(..., description="Para filtrar as receitas"),
            ),
            card_account_out=(
                CardEnum|None,
                Field(..., description="Para filtrar os gastos"),
            ),
            category=(
                CategoriesEnum|None,
                Field(..., description="Filtrar Categoria"),
            ),
            macro_category=(
                MacroCategoriesEnum|None,
                Field(..., description="Filtrar Categoria Macro"),
            ),
            month=(
                MonthsEnum|None,
                Field(..., description="Filtrar o Mês"),
            ),
            transaction_type=(
                TransactionType|None,
                Field(..., description="Filtrar o tipo de transação"),
            ),
            cursor=(str | None, Field(..., description="Ao fazer uma busca, se tiver mais registros esse atributo podera ser retornado, e seja solicitado mais dados para a mesma consulta, envie esse cursor junto para pegar a proxima pagina.")),
            page_size=(int, Field(..., description="O padrão e 25 para a quantidade de registros retornados.")),
        )

        tool = SearchTransactionV2()
        tool._notion_user_data=notion_user_data
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            hasPaid = parms['args']['hasPaid']
            card_account_enter = parms['args']['card_account_enter']
            card_account_out = parms['args']['card_account_out']
            category = parms['args']['category']
            macro_category = parms['args']['macro_category']
            month = parms['args']['month']
            transaction_type = parms['args']['transaction_type']
            cursor = parms['args']['cursor']
            page_size = parms['args']['page_size']

            month_id = await self._notion_user_data.get_data_id(UserDataTypes.MONTHS, month)
            card_account_enter_id = await self._notion_user_data.get_data_id(UserDataTypes.CARDS, card_account_enter)
            card_account_out_id = await self._notion_user_data.get_data_id(UserDataTypes.CARDS, card_account_out)
            category_id = await self._notion_user_data.get_data_id(UserDataTypes.CATEGORIES, category)
            marco_category_id = await self._notion_user_data.get_data_id(UserDataTypes.MACRO_CATEGORIES, macro_category)

            transactions = notion_access.new_get_transactions(
                name,
                hasPaid,
                card_account_enter_id,
                card_account_out_id,
                category_id,
                marco_category_id,
                month_id,
                transaction_type,
                cursor,
                page_size
            )

            return ToolMessage(
                content=transactions,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
        
if __name__ == "__main__":

    import asyncio

    async def test():
        tool = await SearchTransactionV2.instantiate_tool(notion_user_data)
        await tool.ainvoke(
            {
                'args': {
                    'name':'Teste',
                    'amount':400,
                    'date':'2025-05-23',
                    'card_or_account':'NuConta',
                    'category':'Diversos',
                    'macro_category':'Não Essencial',
                    'month':'2025 - Maio',
                }
            },
            {}
        )
    asyncio.run(test())
