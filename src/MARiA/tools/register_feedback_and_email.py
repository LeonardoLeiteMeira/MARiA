from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.memory import Database

class RegisterFeedbackAndEmailInput(BaseModel):
    name: str|None = Field(description="Nome completo da pessoa usuaria")
    email: str|None = Field(description="Email da pessoa usuaria")
    feedback: str|None = Field(description="Feedback da pessoa usuaria")
    contacted: bool|None = Field(description="Tag para indicar se a pessoa usuaria deseja ser contactada no futuro ou nao")


class RegisterFeedbackAndEmail(BaseTool):
    name: str = "register_feedback_and_email"
    description: str = "Registrar feedback e email do usuário"
    args_schema: Type[BaseModel] = RegisterFeedbackAndEmailInput
    repository: Type[Database] = None

    def __init__(self, repository:Database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = repository

    def _run(self, name: str = None, email:str = None, feedback:str = None, contacted:bool = False,*args, **kwargs) -> list[dict]:
        pass
        
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        # from ..notion_repository import notion_access
        try:
            name = parms['args']['name']
            email = parms['args']['email']
            feedback = parms['args']['feedback']
            contacted = parms['args']['contacted']
            thread_id = config['metadata']['thread_id']

            print(name, email, feedback, contacted)
            await self.repository.finish_user_feedback_by_thread_id(thread_id)
            return ToolMessage(
                content=True,
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("RegisterFeedbackAndEmail - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução {e}",
                tool_call_id=parms['id'],
            )
