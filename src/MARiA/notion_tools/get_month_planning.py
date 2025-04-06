from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class GetMonthPlanningInput(BaseModel):
    month_id: str = Field(description='Id do mes para ser buscado')


class GetMonthPlanning(BaseTool):
    name: str = "buscar_planejamento_mes"
    description: str = "Para buscar o planejamento de gastos para um determinado mês. Um planejamento é a seleção de categorias com valor planejado e um calculo do valor gasto. Aqui retorna o acompanhamento de gastos para cada categoria planejada."
    args_schema: Type[BaseModel] = GetMonthPlanningInput

    def _run(self, month_id: str, *args, **kwargs) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            return notion_access.get_planning_by_month(month_id)
        except Exception as e:
            return str(e)
