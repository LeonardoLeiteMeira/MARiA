from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig

class SearchTransactionsInput(BaseModel):
    cursor: str | None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")
    page_size: int = Field(description="Especifica a quantidade de registros por página. O valor padrão é 30 - caso não especificado, mas voce pode escolher de acordo com a necessidade. Para pegar a proxima pagina é necessário usar o 'next_cursor' como 'cursor' da proxima busca.")
    filter: dict | None = Field(
        description="""
        Usado para fazer filtros com combinações logicas usando 'and' e 'or' e os NOMES das propriedaes (não IDs como em 'properties'). 
        Cada operador lógico recebe uma lista de objetos, que contem a 'property' que o filtro vai ser aplicado e o tipo da propriedade com o valor.
        Exemplo: Abaixo tem a busca em que o campo 'MesData' do tipo 'date' deve ser 'on_or_after' um valor 'year' especificado, ou ('or') a propriedade 'Tags' "contains" a tag 'A'
            {
                'and':[
                    {
                        'property': 'MesData',
                        'date': {'on_or_after': f"{year}"},
                    },
                    {
                        'or': [
                            {
                                "property": "Tags",
                                "contains": "A"
                            }
                        ]
                    }
                ]
            }
                                
        Para saber os NOMES das propriedades e os tipos corretos, é necessário entender corretamente a estrutura da tabela de transações!
    """)
    properties: list | None = Field(
        description="""
            Recebe uma lista de IDs de propriedades (lidos do esquema da tabela), e faz com que sejam retornadas apenas aquelas propriedades.
            Para saber os IDs das propriedades corretamnete é necessário entender a estrutura da tabela de transações!
        """)


class SearchTransactions(BaseTool):
    name: str = "buscar_transacoes"
    description: str = "Útil quando é necessário buscar palas transações mais recentes"
    args_schema: Type[BaseModel] = SearchTransactionsInput

    def _run(
            self,
            cursor: str = None,
            page_size: int = None,
            filter: dict = None,
            properties: list = None,
            *args, **kwargs) -> list[dict]:
        pass
        
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ..notion_repository import notion_access
        try:
            cursor = parms['args']['cursor']
            page_size = parms['args']['page_size']
            filter = parms['args']['filter']
            properties = parms['args']['properties']

            transactions =  notion_access.get_transactions(cursor, page_size, filter, properties)

            if transactions == None:
                return ToolMessage(
                    content='Nenhum registro encontrado! Verifique a busca.',
                    tool_call_id=parms['id'],
                )
        
            return ToolMessage(
                content=transactions,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("GetMonths - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução {e}",
                tool_call_id=parms['id'],
            )
