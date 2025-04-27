from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Optional, Type
from langchain_core.messages.tool import ToolMessage
from langchain_core.runnables import RunnableConfig
from MARiA.memory import Database

class FinishedTestPeriodInput(BaseModel):
    pass


class FinishedTestPeriod(BaseTool):
    name: str = "finished_test_period"
    description: str = "Caso o usuaário não queira dar feedback ou informar o email apés algumas interações, é importante finalizar o périodo de testes por essa ferramenta!"
    args_schema: Type[BaseModel] = FinishedTestPeriodInput
    repository: Type[Database] = None

    def __init__(self, repository:Database, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repository = repository

    def _run(self, *args, **kwargs) -> list[dict]:
        pass
        
    async def ainvoke(self, parms:dict, config: Optional[RunnableConfig] = None, *args, **kwargs) -> ToolMessage:
        try:
            thread_id = config['metadata']['thread_id']
            await self.repository.finish_user_feedback_by_thread_id(thread_id)
            return ToolMessage(
                content="Finalizado o periodo de testes desse usuário.",
                tool_call_id=parms['id'],
            )
        except Exception as e:
            print("FinishedTestPeriod - Ocorreu um erro: ", e)
            return ToolMessage(
                content=f"Ocorreu um erro na execução. Verifique os dados e tente novamente. Segue o erro para ajudar a entender: {e}",
                tool_call_id=parms['id'],
            )
