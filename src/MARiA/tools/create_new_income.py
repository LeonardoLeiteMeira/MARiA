from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type, Any, cast
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from pydantic import create_model, Field
from MARiA.tools.tool_interface import ToolInterface
from pydantic import PrivateAttr
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type

class CreateNewIncome(ToolInterface):
    name: str = "criar_nova_transacao_de_entrada"
    description: str = "Cria uma nova transação de entrada com os dados fornecidos - se o usuário não fornecer nenhum parâmetro, é necessário perguntar. Retorna a trasação criada."
    args_schema: Type[BaseModel] | None = None
    __state: State = PrivateAttr()
    __notion_tool: NotionTool = PrivateAttr()

    def __init__(self, state: State, notion_tool: NotionTool, **data: Any) -> None:
        super().__init__(**data)
        self.__state = state
        self.__notion_tool = notion_tool

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        return None


    @classmethod
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'CreateNewIncome':
        cards = get_state_records_by_type(state, UserDataTypes.CARDS_AND_ACCOUNTS)
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)

        from enum import Enum
        CardEnum = Enum(  # type: ignore[misc]
            "CardEnum",
            {card["Name"].upper(): card["Name"] for card in cards},
        )
        MonthsEnum = Enum(  # type: ignore[misc]
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
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

        tool = CreateNewIncome(state=state, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(
        self,
        input: str | dict[Any, Any] | ToolCall,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> ToolMessage:
        try:
            parms = cast(dict[str, Any], input)
            name = parms['args']['name']
            amount = parms['args']['amount']
            date = parms['args']['date']
            card_or_account = parms['args']['card_or_account']
            month = parms['args']['month']
            hasPaid = parms['args']['hasPaid'] if 'hasPaid' in parms['args'] else True

            month_id = get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)
            card_id = get_data_id_from_state(self.__state, UserDataTypes.CARDS_AND_ACCOUNTS, card_or_account)

            new_income = await self.__notion_tool.create_income(
                name = name,
                month_id = cast(str, month_id),
                amount = amount,
                date = date,
                card_id = cast(str, card_id),
                hasPaid = hasPaid,
            )
            return ToolMessage(
                content=cast(Any, new_income),
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
