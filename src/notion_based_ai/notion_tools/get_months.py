from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio
# from notion_based_ai.notion_types import Database

class GetMonthsInput(BaseModel):
    year: int = Field(description="O ano do mês que deve ser listado")
    property_ids: list[str] = Field(
        description="""
            "Uma lista de IDs de propriedades a serem retornadas.
            Por padrão, o ID do 'title' já está incluído, mas se você desejar propriedades adicionais, 
            é necessário ler a estrutura e especificar os IDs aqui.
            """)


class GetMonths(BaseTool):
    name: str = "buscar_meses"
    description: str = "Lista os meses criados pelo usuário para agrupar transações por ano. É possível especificar mais propriedades (por id) a serem retornadas."
    args_schema: Type[BaseModel] = GetMonthsInput

    def _run(self, year:int, property_ids: list[str] = [],*args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun(year, property_ids))

    async def _arun(
        self,
        year:int,
        property_ids: list[str] = [],
        *args, **kwargs
    ) -> list[dict]:
        from ..notion_repository import notion_transactio_repository
        return notion_transactio_repository.get_months_by_year(year, property_ids)