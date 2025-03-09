from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

from notion_based_ai.notion_types import Database

class CreateNewTransactionInput(BaseModel):
    name: str = Field(description="Nome escolhido pelo usuário para identificar a transação")
    amount: float = Field(description="Valor da transação")
    date: str = Field(description="Data da transação")
    card: str = Field(description="Id de um Cartão usado para a transação")
    category: str = Field(description="Id de uma Categoria válida para classificar a transação")
    month: str = Field(description="Id de um Mês válido para classificar a transação")
    type: str = Field(description="Id de um Tipo válido para classificar a transação")


class CreateNewTransaction(BaseTool):
    name: str = "criar_nova_transacao"
    description: str = "Cria uma nova transação com os dados fornecidos - se o usuário não fornecer nenhum parâmetro, é necessário perguntar. É necessário verificar a estrutura do banco de dados."
    args_schema: Type[BaseModel] = CreateNewTransactionInput

    def _run(self, name: str,amount: float,date: str,card: str,category: str,month: str,type: str, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun(
            name,
            amount,
            date,
            card,
            category,
            month,
            type
        ))

    async def _arun(self,name: str,amount: float,date: str,card: str,category: str,month,type,*args, **kwargs) -> list[dict]:
        print({
            'name': name,
            'amount': amount,
            'date': date,
            'card': card,
            'category': category,
            'month': month,
            'type': type
        })
        from ..notion_repository import notion_transactio_repository
        # return notion_transactio_repository.