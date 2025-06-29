# from pydantic import BaseModel, Field
# from langchain_core.tools import BaseTool
# from typing import Optional, Type
# from langchain_core.messages.tool import ToolMessage
# from langchain_core.runnables import RunnableConfig

# class GetMonthsInput(BaseModel):
#     year: int | None = Field(description="O ano do mês que deve ser listado. O default e None, e serão listados os meses desse ano!")
#     property_ids: list[str] = Field(
#         description="""
#             "Uma lista de IDs de propriedades a serem retornadas.
#             Por padrão, o ID do 'title' já está incluído, mas se você desejar propriedades adicionais, 
#             é necessário ler a estrutura e especificar os IDs aqui, ou seja, e necessario ler a estrutura da tabela antes.
#             """)


# class GetMonths(BaseTool):
#     name: str = "buscar_meses"
#     description: str = "Lista os meses criados pelo usuário para agrupar transações por ano. É possível especificar mais propriedades (por id) a serem retornadas."
#     args_schema: Type[BaseModel] = GetMonthsInput

#     def __init__(self, *args , **kwargs):
#         super().__init__(*args, **kwargs)

#     def _run(self, year:int, property_ids: list[str] = [],*args, **kwargs):
#         pass

#     async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
#         from ..notion_repository import notion_access
#         try:
#             year = parms['args']['year']
#             properties = parms['args']['property_ids']

#             data = notion_access.get_months_by_year(year, properties)
#             if data == None:
#                 return ToolMessage(
#                     content='Nenhum registro encontrado! Verifique os parametros da busca. Lembre-se que o parametro property_ids deve ser o id das propriedade e nao os nomes.',
#                     tool_call_id=parms['id'],
#                 )

#             return ToolMessage(
#                 content=data,
#                 tool_call_id=parms['id'],
#             )
#         except Exception as e:
#             print("GetMonths - Ocorreu um erro: ", e)
#             return ToolMessage(
#                 content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Lembre-se que o parametro property_ids deve ser o id das propriedade e nao os nomes. Segue o erro para ajudar a entender: {e}",
#                 tool_call_id=parms['id'],
#             )

