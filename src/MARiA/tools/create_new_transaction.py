from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.notion_types import NotionDatabaseEnum

class CreateNewOutTransactionInput(BaseModel):
    name: str = Field(description="Nome escolhido pelo usuário para identificar a transação de saída")
    amount: float = Field(description="Valor da transação")
    date: str = Field(description="Data da transação no formato iso")
    cardId: str = Field(description="Id de um Cartão ou Conta usado para a transação")
    categoryId: str = Field(description="Id de uma Categoria válida para classificar a transação")
    monthId: str = Field(description="Id de um Mês válido para classificar a transação")
    typeId: str = Field(description="Id de um Tipo válido para classificar a transação")


#TODO Problemas (Esse problemas serão resolvidos com um workflow especifico)
# 1. Esta inventando infos - Criou no cartao nda nubank sem eu ter falado isso e o typo colocou como essencial sem eu dizer
# 2. Acredito que tenha muitas etapas para fazer essa busca - Simplificar o processo de criacao de transacao

class CreateNewOutTransaction(BaseTool):
    name: str = "criar_nova_transacao_de_saida"
    description: str = "Cria uma nova transação de saída com os dados fornecidos - se o usuário não fornecer nenhum parâmetro, é necessário perguntar. É necessário verificar a estrutura do banco de dados. Lembre-se de passar os IDs corretos e não os nomes."
    args_schema: Type[BaseModel] = CreateNewOutTransactionInput

    def _run(self, name: str,amount: float,date: str,cardId: str,categoryId: str,monthId: str,typeId: str, *args, **kwargs) -> ToolMessage:
        pass

    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        from ..notion_repository import notion_access
        try:
            name = parms['args']['name']
            amount = parms['args']['amount']
            date = parms['args']['date']
            cardId = parms['args']['cardId']
            categoryId = parms['args']['categoryId']
            monthId = parms['args']['monthId']
            typeId = parms['args']['typeId']

            notion_access.create_out_transaction(
                name,
                monthId,
                amount,
                date,
                cardId,
                categoryId,
                typeId
            )
            return ToolMessage(
                content="Criado com sucesso",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução: {e}",
                tool_call_id=parms['id'],
            )
