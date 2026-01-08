from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from external.notion.enum import UserDataTypes, GlobalTransactionType
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type

from typing import Union, Any, cast

class CreateNewTransaction(ToolInterface):
    description: str = """
Responsável por criar uma transação e retornar ela com o id.
Cada tipo de transação deve ter seus dados ideias para manter a consistencia dos dados:
- Uma saida teve ter o campo 'conta de saida' preenchido, mas nao deve ter o campo 'conta de entrada';
- Uma entrada teve ter o campo 'conta de entrada' preenchido, mas nao deve ter o campo 'conta de saida';
- Uma transaferencia ou pagamento de fatura do cartão teve ter ambos os campos 'conta de entrada' e 'conta de saida' preenchidos, pois saiu de algum lugar e foi para outro;
- Apenas saidas tem categorias e macro-categorias!;
"""
    name: str = "criar_nova_transacao"
    args_schema: Type[BaseModel] | None = None
    __state: State = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data: Any):
        super().__init__(**data)
        self.__state = state
        self.__notion_tool = notion_tool

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        pass


    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'CreateNewTransaction':
        cards = get_state_records_by_type(state, UserDataTypes.CARDS_AND_ACCOUNTS)
        categories = get_state_records_by_type(state, UserDataTypes.CATEGORIES)
        macroCategories = get_state_records_by_type(state, UserDataTypes.MACRO_CATEGORIES)
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)

        from enum import Enum
        CardEnum = Enum(
            "CardEnum",
            {card["Name"].upper(): card["Name"] for card in cards},
        )
        CategoriesEnum = Enum(
            "CategoryEnum",
            {category["Name"].upper(): category["Name"] for category in categories},
        )
        MacroCategoriesEnum = Enum(
            "macroCategoryEnum",
            {macro["Name"].upper(): macro["Name"] for macro in macroCategories},
        )
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
        )

        InputModel = create_model(
            "CreateNewOutTransactionInputDynamic",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            amount=(float, Field(..., description="Valor da transação")),
            date=(str, Field(..., description="Data ISO da transação. Use a data correta. Se o usuario nao fornecer use a de hoje!")),
            hasPaid=(bool, Field(default=True, description="Se a transação foi paga ou não. Se o usuário não informar, deve ser True!")),
            enter_account=(
                Optional[CardEnum],
                Field(..., description="Cartão ou conta onde o dinheiro entrou."),
            ),
            debit_account=(
                Optional[CardEnum],
                Field(..., description="Cartão ou conta de onde o dinheiro saiu."),
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
                Field(..., description="Mês ou gestão em que ocorreu a transação."),
            ),
            transaction_type=(
                GlobalTransactionType,
                Field(..., description="Tipo da transação que deve ser criada.")
            )
        )

        tool = CreateNewTransaction(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, input: Union[str, dict, ToolCall], config: Optional[RunnableConfig] = None, **kwargs: Any) -> ToolMessage:
        try:
            input_dict: dict = cast(dict, input)
            args_data: dict = cast(dict, input_dict['args'])

            validation_result = self.__validate_transaction_data(args_data, input_dict['id'])

            if validation_result is not None:
                return validation_result

            name = args_data['name']
            amount = args_data['amount']
            month = args_data['month']
            date = args_data['date']
            transaction_type: GlobalTransactionType = GlobalTransactionType(args_data['transaction_type'])

            enter_account = args_data.get('enter_account')
            debit_account = args_data.get('debit_account')

            category = args_data.get('category')
            macro_category = args_data.get('macro_category')
            hasPaid: bool = args_data.get('hasPaid', True)

            month_id = get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)
            enter_account_id = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, enter_account)
            debit_account_id = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, debit_account)
            category_id = get_data_id_from_state(self.__state, UserDataTypes.CATEGORIES, category) if category else None
            macro_category_id = get_data_id_from_state(self.__state, UserDataTypes.MACRO_CATEGORIES, macro_category) if macro_category else None

            if month_id is None:
                return ToolMessage(
                    content="Wasn't possible to identify id of month",
                    tool_call_id=input_dict['id'],
                )

            new_transaction = await self.__notion_tool.create_new_transaction(
                name,
                month_id,
                amount,
                date,
                enter_account_id,
                debit_account_id,
                category_id,
                macro_category_id,
                transaction_type,
                hasPaid,
            )
            return ToolMessage(
                content='Criado com sucesso!',
                artifact=new_transaction,
                tool_call_id=input_dict['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, input_dict['id'])
        
    def __validate_transaction_data(self, args_data: dict, call_id: str) -> ToolMessage | None:
        name = args_data.get('name')
        amount = args_data.get('amount')
        month = args_data.get('month')
        date = args_data.get('date')
        transaction_type_str: GlobalTransactionType | None = args_data.get('transaction_type', None)

        if name is None or amount is None or month is None or date is None or transaction_type_str is None:
            return ToolMessage(
                content='Some mandatory field is None. name or amout or month or date or transaction_type',
                tool_call_id=call_id,
            )
        
        transaction_type = GlobalTransactionType(transaction_type_str)

        enter_account = args_data.get('enter_account')
        debit_account = args_data.get('debit_account')

        category = args_data.get('category')
        macro_category = args_data.get('macro_category')

        match (transaction_type):
            case GlobalTransactionType.INCOME:
                if debit_account or category or macro_category:
                    return ToolMessage(
                        content=f"{transaction_type.value} doesn't have debit_account or category or macro_category.",
                        tool_call_id=call_id,
                    )
            case GlobalTransactionType.OUTCOME:
                if enter_account:
                    return ToolMessage(
                        content=f"{transaction_type.value} doesn't have enter_accoun.",
                        tool_call_id=call_id,
                    )
                
                if category is None or macro_category is None:
                    return ToolMessage(
                        content=f"{transaction_type.value} should have category and macro category.",
                        tool_call_id=call_id,
                    )
            case GlobalTransactionType.TRANSFER | GlobalTransactionType.PAY_CREDIT_CARD:
                if enter_account is None or debit_account is None:
                    return ToolMessage(
                        content=f"{transaction_type.value} should have both enter_account and debit_account.",
                        tool_call_id=call_id,
                    )

                if category is not None or macro_category is not None:
                    return ToolMessage(
                        content=f"{transaction_type.value} shouldn't have category and macro category.",
                        tool_call_id=call_id,
                    )
            case _:
                return ToolMessage(
                    content={
                        'status': 'Error',
                        'error_message': f"Invalid transaction type."
                    },
                    tool_call_id=call_id,
                )

        return None
        
# if __name__ == "__main__":

#     import asyncio

#     async def test():
#         tool = await CreateNewTransaction.instantiate_tool(notion_user_data)
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
