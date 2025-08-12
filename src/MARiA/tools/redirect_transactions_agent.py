from enum import Enum
from pydantic import BaseModel, Field
from typing import Type
from langchain_core.messages.tool import ToolMessage
from pydantic import create_model, Field

from .tool_interface import ToolInterface
from .tool_type_enum import ToolType

class TransactionOperationEnum(Enum):
    CREATE_INCOME = 'CREATE_INCOME'
    CREATE_OUTCOME = 'CREATE_OUTCOME'
    CREATE_TRANSFER = 'CREATE_TRANSFER'
    PAY_CREDIT_CARD = "PAY_CREDIT_CARD"
    QUERY_DATA = "QUERY_DATA"
    UPDATE_DATA = "UPDATE_DATA"

class RedirectTransactionsAgent(ToolInterface):
    name: str = "transactions_agent"
    description: str = "Agentes responsaveis por lidar com tudo relacionado a transações - Cada Operação é um agente. Criar gastos, transferencias, receitas, além de conseguir listar as transações de acordo com a solicitação do usuário."
    args_schema: Type[BaseModel] = create_model(
        "RedirectTransactionsAgentInput",
        query=(str, Field(..., description="Descricao exata do que o usuario quer. Seja bem especifico e inclua detalhes relevantes para que esse agente entenda bem o que deve ser feito, informando não apenas dados que o usuário passou mas também dados do sistem (id por exemplo), quando for relevante.")),
        operation_type=(TransactionOperationEnum, Field(..., description="Informe qual o agente em especifico que deve ser selecionado dentre as opções."))
    )
    tool_type: ToolType = ToolType.AGENT_REDIRECT

    def _run(self, name: str, *args, **kwargs) -> ToolMessage:
        pass

    @classmethod
    async def instantiate_tool(cls, notion_user_data: None, notion_tool: None) -> 'RedirectTransactionsAgent':
        return RedirectTransactionsAgent()