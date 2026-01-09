from pydantic import BaseModel, Field
from typing import Any, Optional, Type, cast
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field, PrivateAttr

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type

class SearchTransactionV2(ToolInterface):
    name: str = "buscar_transacoes_com_parametros"
    description: str = "Fazer busca de transacoes com base nas informacoes que o usuario passar. Use apenas as informações que o usuário passar, o que ele não passar deixe como None"
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
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'SearchTransactionV2':
        cards = get_state_records_by_type(state, UserDataTypes.CARDS_AND_ACCOUNTS)
        categories = get_state_records_by_type(state, UserDataTypes.CATEGORIES)
        macroCategories = get_state_records_by_type(state, UserDataTypes.MACRO_CATEGORIES)
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)
        transaction_types = state.get("transaction_types")
        if not transaction_types:
            transaction_enum = notion_tool.ger_transaction_types()
            transaction_types = [member.value for member in transaction_enum]

        from enum import Enum
        CardEnum = Enum(  # type: ignore[misc]
            "CardEnum",
            {card["Name"].upper(): card["Name"] for card in cards},
        )
        CategoriesEnum = Enum(  # type: ignore[misc]
            "CategoryEnum",
            {category["Name"].upper(): category["Name"] for category in categories},
        )
        MacroCategoriesEnum = Enum(  # type: ignore[misc]
            "macroCategoryEnum",
            {macro["Name"].upper(): macro["Name"] for macro in macroCategories},
        )
        MonthsEnum = Enum(  # type: ignore[misc]
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
        )
        TransactionTypeEnum = Enum(  # type: ignore[misc]
            "TransactionTypeEnum",
            {value.upper().replace(" ", "_"): value for value in transaction_types},
        )

        InputModel = create_model(
            "CreateNewOutTransactionInputDynamic",
            name=(str | None, Field(..., description="Filtrar por nome")),
            has_paid=(bool | None, Field(..., description="Filtar transações pagas ou pendentes. True são as já pagas, False são as pendentes.")),
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
                TransactionTypeEnum | None,
                Field(..., description="Filtrar o tipo de transação"),
            ),
            cursor=(str | None, Field(..., description="Ao fazer uma busca, se tiver mais registros esse atributo podera ser retornado, e seja solicitado mais dados para a mesma consulta, envie esse cursor junto para pegar a proxima pagina.")),
            page_size=(int, Field(..., description="O padrão e 25 para a quantidade de registros retornados.")),
        )

        tool = SearchTransactionV2(state=state, notion_tool=notion_tool)
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
            args_data = input_dict['args']
            name = args_data.get('name', None)
            has_paid = args_data.get('has_paid', None)
            card_account_enter = args_data.get('card_account_enter', None)
            card_account_out = args_data.get('card_account_out', None)
            category = args_data.get('category', None)
            macro_category = args_data.get('macro_category', None)
            month = args_data.get('month', None)
            transaction_type = args_data.get('transaction_type', None)
            cursor = args_data.get('cursor', None)
            page_size = args_data.get('page_size', None)

            month_id = get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)
            card_account_enter_id = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, card_account_enter)
            card_account_out_id = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, card_account_out)
            category_id = get_data_id_from_state(self.__state, UserDataTypes.CATEGORIES, category)
            macro_category_id = get_data_id_from_state(self.__state, UserDataTypes.MACRO_CATEGORIES, macro_category)

            transactions = await self.__notion_tool.get_transactions(
                name,
                has_paid,
                card_account_enter_id,
                card_account_out_id,
                category_id,
                macro_category_id,
                month_id,
                transaction_type,
                cursor,
                page_size
            )

            return ToolMessage(
                content=cast(str, transactions),
                tool_call_id=input_dict['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, input_dict['id'])
        
# if __name__ == "__main__":

#     import asyncio

#     async def test():
#         tool = await SearchTransactionV2.instantiate_tool(notion_user_data)
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
