# from pydantic import BaseModel, Field
# from langchain_core.tools import BaseTool
# from typing import Optional, Type
# from langchain_core.messages.tool import ToolMessage
# from langchain_core.runnables import RunnableConfig

# class GetMonthPlanningInput(BaseModel):
#     month_id: str = Field(description='Id do mes para ser buscado')


# class GetMonthPlanning(BaseTool):
#     name: str = "buscar_planejamento_mes"
#     description: str = "Para buscar o planejamento de gastos para um determinado mês. Um planejamento é a seleção de categorias com valor planejado e um calculo do valor gasto. Aqui retorna o acompanhamento de gastos para cada categoria planejada."
#     args_schema: Type[BaseModel] = GetMonthPlanningInput

#     def _run(self, month_id: str, *args, **kwargs) -> list[dict]:
#         pass
    
#     async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
#         from ..notion_repository import notion_access
#         try:
#             month_id = parms['args']['month_id']
#             planning = notion_access.get_planning_by_month(month_id)
#             return ToolMessage(
#                 content=planning,
#                 tool_call_id=parms['id'],
#             )
#         except Exception as e:
#             print("GetMonthPlanning - Ocorreu um erro: ", e)
#             return ToolMessage(
#                 content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Lembre-se que aqui precisa ser passado o ID do mês. Segue o erro para ajudar a entender: {e}",
#                 tool_call_id=parms['id'],
#             )