from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_types import NotionDatabaseEnum

class GetUserCardsInput(BaseModel):
    cursor: str|None = Field(description="Usado para buscar os dados paginados. Deve ser informado apenas quando é necessário busca mais de uma página, e a busca anterior retornou o 'has_more' como true.")
    properties: list | None = Field(
        description="""
            Recebe uma lista de IDs de propriedades (lidos do esquema da tabela), e faz com que sejam retornadas apenas aquelas propriedades.
            Para saber os IDs das propriedades corretamnete é necessário entender a estrutura da tabela de transações!
            Para buscar os valores de conta/cartão é necessário informar o Id dessas propriedades (colunas da tabela).
        """)


class GetUserCards(BaseTool):
    name: str = "buscar_contas_e_cartoes"
    description: str = "Listar todas as possíveis contas e cartões que podem ser usadas para uma transação"
    args_schema: Type[BaseModel] = GetUserCardsInput

    def _run(self, cursor: str = None, *args, **kwargs) -> list[dict]:
        pass

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ..notion_repository import notion_access
        try:
            cursor = parms['args']['cursor']
            properties = parms['args']['properties']
            user_cards = notion_access.get_simple_data(NotionDatabaseEnum.CARDS, cursor, properties)

            return ToolMessage(
                content=user_cards,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("GetMonths - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução {e}",
                tool_call_id=parms['id'],
            )