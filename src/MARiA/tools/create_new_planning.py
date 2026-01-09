from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type, Any, cast
from langchain_core.messages.tool import ToolMessage, ToolCall
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.tool_interface import ToolInterface
from external.notion import NotionTool
from external.notion.enum import UserDataTypes
from MARiA.graph.state import State
from MARiA.tools.state_utils import get_data_id_from_state, get_state_records_by_type

class CreateNewPlanning(ToolInterface):
    name: str = "criar_novo_planejamento"
    description: str = "Criar um novo planejamento associado um mes. Retorna os planejamentos criados."
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
    async def instantiate_tool(cls, state: State, notion_tool: NotionTool) -> 'CreateNewPlanning':
        months = get_state_records_by_type(state, UserDataTypes.MONTHS)
        categories = get_state_records_by_type(state, UserDataTypes.CATEGORIES)

        from enum import Enum
        CategoriesEnum = Enum(  # type: ignore[misc]
            "CategoryEnum",
            {category["Name"].upper(): category["Name"] for category in categories},
        )
        MonthsEnum = Enum(  # type: ignore[misc]
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in months},
        )

        InputModelUnit: type[BaseModel] = create_model(
            "CreateNewOutTransactionInputDynamic",
            name=(str | None, Field(..., description="Apenas um nome para identificar. Constuma ser o mesmo valor da categoria, mas pode ser outra da preferencia.")),
            category=(
                CategoriesEnum|None,
                Field(..., description="Categoria para ser acompanhada."),
            ),
            month=(
                MonthsEnum|None,
                Field(..., description="Mes que esse planejamento entra."),
            ),
            amount=(float, Field(..., description="Valor do orçamento para essa categoria nesse mês.")),
            text=(str, Field(..., description="Texto de observação sobre esse planejamento. Pode ser algo do usuário ou percepção sua.")),
        )

        InputModel = create_model(
            "CreateNewOutTransactionInputDynamic",
            plans=(list[InputModelUnit], Field(..., description="Lista de planejamentos a serem criados"))  # type: ignore[valid-type]
        )


        tool = CreateNewPlanning(state=state, notion_tool=notion_tool)
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
            plans = parms['args']['plans']

            if not isinstance(plans, list):
                return ToolMessage(
                    content="Error: plans should be a list",
                    tool_call_id=parms['id'],
                )
            
            plans_created: list[dict[str, Any]] = []
            
            for plan in plans:
                name = plan['name']
                category = plan['category']
                month = plan['month']
                amount = plan['amount']
                text = plan['text']
        
                month_id = get_data_id_from_state(self.__state, UserDataTypes.MONTHS, month)
                category_id = get_data_id_from_state(self.__state, UserDataTypes.CATEGORIES, category)

                # One post for each item because notion api doesn't support batch creation
                plans_created.append(
                    await self.__notion_tool.create_plan(
                        name,
                        cast(str, month_id),
                        cast(str, category_id),
                        amount,
                        text
                    )
                ) 

            return ToolMessage(
                content=cast(list[str | dict[Any, Any]], plans_created),
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return self.handle_tool_exception(e, parms['id'])
        
# if __name__ == "__main__":

#     import asyncio

#     async def test():
#         tool = await CreateNewPlanning.instantiate_tool(notion_user_data)
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
