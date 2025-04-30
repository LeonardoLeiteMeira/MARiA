import aiohttp
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.memory import Database
from enum import Enum

class ProductEnum(str, Enum):
    family = "family"
    business = "business"
    both = "both"

class RegisterFeedbackAndEmailInput(BaseModel):
    name: str|None = Field(description="Nome completo da pessoa usuaria")
    email: str|None = Field(description="Email da pessoa usuaria")
    feedback: str|None = Field(description="Descreva aqui como foi a interação com o usuário em no máximo 3 frases")
    contacted: bool|None = Field(description="Tag para indicar se a pessoa usuaria deseja ser contactada no futuro ou nao")
    product: ProductEnum = Field(description="Nome do produto da pessoa usuaria - deve ser family, business ou both")


class RegisterFeedbackAndEmail(BaseTool):
    name: str = "register_feedback_and_email"
    description: str = "Registrar feedback e email do usuário"
    args_schema: Type[BaseModel] = RegisterFeedbackAndEmailInput
    repository: Type[Database] = None

    def __init__(self, repository:Database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = repository

    def _run(self, *args, **kwargs) -> list[dict]:
        pass
        
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            name = parms['args']['name']
            email = parms['args']['email']
            feedback = parms['args']['feedback']
            product = parms['args']['product']
            contacted = parms['args']['contacted']
            contacted = parms['args']['contacted']
            thread_id = config['metadata']['thread_id']

            if contacted:
                register_lead_url = 'https://6roa5y2ufh.execute-api.us-east-1.amazonaws.com/maria_lead/maria_lead'
                data = {
                    'name': name,
                    'email': email,
                    'message': feedback,
                    'product': product,
                    'lead_source': 'websummit',
                    'honey_pot': ''
                }
                session = aiohttp.ClientSession()
                await session.put(register_lead_url, json=data, headers={'Content-Type': 'application/json'})
                await session.close()

            await self.repository.finish_user_feedback_by_thread_id(thread_id)

            return ToolMessage(
                content="Registro com sucesso! IMPORTANTE: Avise ao usuário que o teste dele finalizou e que ele não terá mais acesso. Entraremos em contato assim que estiver disponível",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("RegisterFeedbackAndEmail - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender:{e}",
                tool_call_id=parms['id'],
            )
