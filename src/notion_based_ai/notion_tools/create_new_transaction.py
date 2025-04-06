from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class CreateNewTransactionInput(BaseModel):
    name: str = Field(description="Nome escolhido pelo usuário para identificar a transação")
    amount: float = Field(description="Valor da transação")
    date: str = Field(description="Data da transação no formato iso")
    cardId: str = Field(description="Id de um Cartão ou Conta usado para a transação")
    categoryId: str = Field(description="Id de uma Categoria válida para classificar a transação")
    monthId: str = Field(description="Id de um Mês válido para classificar a transação")
    typeId: str = Field(description="Id de um Tipo válido para classificar a transação")


#TODO Problemas
# 1. Esta inventando infos - Criou no cartao nda nubank sem eu ter falado isso e o typo colocou como essencial sem eu dizer
# 2. Acredito que tenha muitas etapas para fazer essa busca - Simplificar o processo de criacao de transacao

class CreateNewTransaction(BaseTool):
    name: str = "criar_nova_transacao"
    description: str = "Cria uma nova transação de saida com os dados fornecidos - se o usuário não fornecer nenhum parâmetro, é necessário perguntar. É necessário verificar a estrutura do banco de dados. Lembre-se de passar os IDs corretos e não os nomes"
    args_schema: Type[BaseModel] = CreateNewTransactionInput

    def _run(self, name: str,amount: float,date: str,cardId: str,categoryId: str,monthId: str,typeId: str, *args, **kwargs) -> list[dict]:
        from ..notion_repository import notion_access
        try:
            notion_access.create_out_transaction(
                name,
                monthId,
                amount,
                date,
                cardId,
                categoryId,
                type
            )
        except Exception as e:
            return str(e)

