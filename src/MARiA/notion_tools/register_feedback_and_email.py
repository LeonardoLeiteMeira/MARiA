from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio
from MARiA.memory import Database
from MARiA.notion_types import NotionDatabaseEnum

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
        # from ..notion_repository import notion_access
        try:
            print(name, email, feedback, contacted)
            # await self.repository.finish_user_feedback(user_id)
            return True
        except Exception as e:
            return str(e)
