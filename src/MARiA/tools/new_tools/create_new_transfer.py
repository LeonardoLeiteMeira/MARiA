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

class CreateNewTransfer(BaseTool, ToolInterface):
    name: str = "criar_nova_transferencia"
    description: str = "Criar uma nova transferencia entre constas ou cartoes do usuario. Usao para pagar cartoes de credito tambem, com uma transferencia de uma conta corrente para um cartao de credito."
    args_schema: Type[BaseModel] = None
    _notion_user_data: NotionUserData = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, **data):
        super().__init__(**data)
        self._notion_user_data = notion_user_data

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData) -> 'CreateNewTransfer':
        user_data = await notion_user_data.get_user_base_data()

        from enum import Enum
        EnterInEnum = Enum(
            "CardInEnum",
            {card["Name"].upper(): card["Name"] for card in user_data.cards['data']},
        )
        OutOfEnum = Enum(
            "CardInEnum",
            {card["Name"].upper(): card["Name"] for card in user_data.cards['data']},
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

        tool = CreateNewTransfer(notion_user_data=notion_user_data)
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

            month_id = await self._notion_user_data.get_data_id(UserDataTypes.MONTHS, month)
            enter_in = await self._notion_user_data.get_data_id(UserDataTypes.CARDS, enter_in)
            out_of = await self._notion_user_data.get_data_id(UserDataTypes.CARDS, out_of)

            notion_access.create_transfer_transaction(
                name,
                month_id,
                amount,
                date,
                enter_in,
                out_of,
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
        
if __name__ == "__main__":

    import asyncio

    async def test():
        tool = await CreateNewTransfer.instantiate_tool(notion_user_data)
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
