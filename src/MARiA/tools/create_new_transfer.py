from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type


class CreateNewTransfer(ToolInterface):
    name: str = "criar_nova_transferencia"
    description: str = "Criar uma nova transferencia entre constas ou cartoes do usuario. Usao para pagar cartoes de credito tambem, com uma transferencia de uma conta corrente para um cartao de credito."
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
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'CreateNewTransfer':
        cards = get_state_records_by_type(state, UserDataTypes.CARDS_AND_ACCOUNTS)
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)

        from enum import Enum
        EnterInEnum = Enum(
            "CardInEnum",
            {card["Name"].upper(): card["Name"] for card in cards},
        )
        OutOfEnum = Enum(
            "CardInEnum",
            {card["Name"].upper(): card["Name"] for card in cards},
        )
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
        )

        InputModel = create_model(
            "CreateNewOutTransactionInputDynamic",
            name=(str, Field(..., description="Nome escolhido para a transação")),
            amount=(float, Field(..., description="Valor da transação")),
            date=(str, Field(..., description="Data ISO da transação")),
            hasPaid=(bool, Field(..., description="Se a transação foi paga ou não. O default é True.")),
            enter_in=(
                EnterInEnum,
                Field(..., description="Para onde o dinheiro está indo. Pode ser uma conta ou um cartão."),
            ),
            out_of=(
                OutOfEnum,
                Field(..., description="Para onde o dinheiro esta indo. Constuma ser sempre uma conta corrente."),
            ),
            month=(
                MonthsEnum,
                Field(..., description="Mês ou gestão em que ocorreu a transação"),
            ),
        )

        tool = CreateNewTransfer(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            amount = parms['args']['amount']
            date = parms['args']['date']
            hasPaid = parms['args']['hasPaid']
            enter_in = parms['args']['enter_in']
            out_of = parms['args']['out_of']
            month = parms['args']['month']

            month_id = get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)
            enter_in = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, enter_in)
            out_of = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, out_of)

            new_transfer = await self.__notion_tool.create_transfer(
                name,
                month_id,
                amount,
                date,
                enter_in,
                out_of,
                hasPaid
            )
            return ToolMessage(
                content=new_transfer,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
        
# if __name__ == "__main__":

#     import asyncio

#     async def test():
#         tool = await CreateNewTransfer.instantiate_tool(notion_user_data)
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
