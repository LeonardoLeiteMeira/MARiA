from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from MARiA.agents.prompts import prompt_maria_initial, prompt_email_collection, prompt_maria_websummit
from MARiA.tools import tools, websummitTools
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from langchain_core.runnables import RunnableConfig
from langchain_core.messages.tool import ToolMessage
import os
import httpx


class SearchDataInput(BaseModel):
        search_text: str = Field(description="Texto em linguagem natural descrevendo a busca que deve ser feita. Por exemplo: 'Busque minha transação mais cara do mês de março' ou 'Busque o meu planejamento de fevereiro'")
        remote_jid: str = Field(description="Dado do whatsapp que vem antes de todoas as mensagens que o usuario envia")

class SearchData(BaseTool):
    name: str = "fazer_busca_nos_dados"
    description: str = "Usa um outro agente para fazer a busca dos dados com base em um texto em linguagem natural. So existe uma fonte de dados seja sucinto."
    args_schema: Type[BaseModel] = SearchDataInput

    def __init__(self, search_model, *args , **kwargs):
        super().__init__(*args, **kwargs)
        self.search_model = search_model
        self.evolution_api_key = os.getenv("AUTHENTICATION_API_KEY")

    def _run(self, search: str, *args, **kwargs) -> list[dict]:
        pass
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            search = parms['args']['search_text']
            remote_jid = parms['args']['remote_jid']
            await self.send_whatsapp_message(remote_jid, "Vou buscar algumas informações, já te retorno.")
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
        

    async def send_whatsapp_message(self, to:str, message: str):
        try:
            base_url = "http://localhost:8080/message/sendText/maria"
            body = {
                "number": to,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": False
                },
                "text": message
            }
            headers = {"apikey": self.evolution_api_key}

            async with httpx.AsyncClient() as client:
                response = await client.post(base_url, json=body, headers=headers)
        except Exception as e:
            print("ERROR TO SEND WHATSAPP MESSAGE: ", e)