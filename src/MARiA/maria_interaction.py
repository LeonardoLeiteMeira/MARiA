from contextlib import _AsyncGeneratorContextManager
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command
from datetime import datetime

from .graph import MariaGraph
from dto import UserAnswerDataDTO
from domain import UserDomain
from repository import UserModel, ThreadModel
from repository.db_models.notion_database_model import NotionDatabaseModel

class MariaInteraction:
    def __init__(self, user_domain: UserDomain, maria_graph: MariaGraph, checkpointer_manager: _AsyncGeneratorContextManager[AsyncPostgresSaver]):
        self.__user_domain = user_domain
        self.__checkpointer = checkpointer_manager
        self.__maria_graph = maria_graph

    async def get_maria_answer(self, user: UserModel, user_input: str) -> str:
        current_thread = await self.__get_current_thread(user.id)
        thread_id_str = str(current_thread.id)
        config = {"configurable": {"thread_id": thread_id_str}}
        now = datetime.now()
        current_time = now.strftime("%I:%M %p, %B %d, %Y")
        user_input_with_name = f"{current_time} - {user.name}: {user_input}"

        async with self.__checkpointer as checkpointer:
            await checkpointer.setup()
            user_notion_databases = await self.__user_domain.get_user_notion_databases_taged(user.id)

            user_answer_data = self.__get_user_answer_data(user, user_notion_databases)
            state_graph = await self.__maria_graph.get_state_graph(user_answer_data)

            compiled = state_graph.compile(checkpointer=checkpointer)
            snapshot = await compiled.aget_state(config, subgraphs=True)

            interrupts = tuple(
                intr
                for task in getattr(snapshot, "tasks", ())
                for intr in getattr(task, "interrupts", ())
            )

            if interrupts:
                cmd = Command(resume=user_input_with_name)
                result = await compiled.ainvoke(cmd, config=config, debug=True)
            else:
                result = await compiled.ainvoke({"user_input": HumanMessage(user_input_with_name)}, config=config, debug=True)
            messages = result["messages"]

        #TODO WIP Multi-agent quando for interrupt nao posso pegar a ultima mensagem, tenho que pegar a query do interrupt
        resp = messages[-1].content
        return resp
    
    async def __get_current_thread(self, user_id: str) -> ThreadModel:
        user_threads = await self.__user_domain.get_user_valid_thread(user_id)
        if len(user_threads) < 1:
            current_thread = await self.__user_domain.create_new_user_thread(user_id) 
        else:
            current_thread = user_threads[0]
        return current_thread
    
    def __get_user_answer_data(self, user: UserModel, user_notion_databases: list[NotionDatabaseModel]) -> UserAnswerDataDTO:
        return UserAnswerDataDTO(
            access_token=user.notion_authorization.access_token,
            user_databases=user_notion_databases,
            use_default_template=user.phone_number!='5531933057272' #TODO como sou apenas eu, manter a sim por enquanto
        )