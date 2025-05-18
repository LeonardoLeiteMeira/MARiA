from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Optional, Type
from langchain_core.runnables import RunnableConfig
from langchain_core.messages.tool import ToolMessage


class SearchDataInput(BaseModel):
    search_text: str = Field(description="Texto em linguagem natural descrevendo a busca que deve ser feita. Por exemplo: 'Busque minha transação mais cara do mês de março' ou 'Busque o meu planejamento de fevereiro'")
    remote_jid: str = Field(description="Dado do whatsapp que vem antes de todoas as mensagens que o usuario envia")

class SearchData(BaseTool):
    name: str = "fazer_busca_nos_dados"
    description: str = "Usa um outro agente para fazer a busca dos dados com base em um texto em linguagem natural. So existe uma fonte de dados seja sucinto."
    args_schema: Type[BaseModel] = SearchDataInput
    search_model: Type[Any] = None

    def __init__(self, search_model, *args , **kwargs):
        super().__init__(*args, **kwargs)
        self.search_model = search_model

    def _run(self, search: str, *args, **kwargs) -> list[dict]:
        pass
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            search = parms['args']['search_text']
            output = await self.search_model.ainvoke({"messages": search})
            final_message = output['messages'][-1].content
            return ToolMessage(
                content=final_message,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
