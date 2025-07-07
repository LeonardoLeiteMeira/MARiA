from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import create_model, Field
from pydantic import PrivateAttr

from MARiA.tools.new_tools.tool_interface import ToolInterface
from external import NotionTool, NotionUserData
from external.enum import UserDataTypes

class CreateNewPlanning(ToolInterface):
    name: str = "criar_novo_planejamento"
    description: str = "Criar um novo planejamento associado um mes"
    args_schema: Type[BaseModel] = None
    __notion_user_data: NotionUserData = PrivateAttr()
    __notion_user_data: NotionTool = PrivateAttr()

    def __init__(self, notion_user_data: NotionUserData, notion_tool: NotionTool, **data):
        super().__init__(**data)
        self.__notion_user_data = notion_user_data
        self.__notion_tool = notion_tool

    def _run(self, *args, **kwargs) -> ToolMessage:
        pass


    @classmethod
    async def instantiate_tool(cls, notion_user_data: NotionUserData, notion_tool: NotionTool) -> 'CreateNewPlanning':
        user_data = await notion_user_data.get_user_base_data()

        from enum import Enum
        CategoriesEnum = Enum(
            "CategoryEnum",
            {category["Name"].upper(): category["Name"] for category in user_data.categories['data']},
        )
        MonthsEnum = Enum(
            "MonthEnum",
            {month["Name"].upper(): month["Name"] for month in user_data.months['data']},
        )

        InputModel = create_model(
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

        tool = CreateNewPlanning(notion_user_data=notion_user_data, notion_tool=notion_tool)
        tool.args_schema = InputModel
        return tool

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            category = parms['args']['category']
            month = parms['args']['month']
            amount = parms['args']['amount']
            text = parms['args']['text']
     
            month_id = await self.__notion_user_data.get_data_id(UserDataTypes.MONTHS, month)
            category_id = await self.__notion_user_data.get_data_id(UserDataTypes.CATEGORIES, category)

            await self.__notion_tool.create_plan(
                name,
                month_id,
                category_id,
                amount,
                text
            )

            return ToolMessage(
                content="Criado com sucesso!",
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
