from .graph import MariaGraph
from contextlib import _AsyncGeneratorContextManager
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage
from domain import UserDomain
from repository import UserModel, ThreadModel
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

class MariaInteraction:
    def __init__(self, user_domain: UserDomain, maria_graph: MariaGraph, checkpointer_manager: _AsyncGeneratorContextManager[AsyncPostgresSaver]):
        self.__user_domain = user_domain
        self.__checkpointer = checkpointer_manager
        self.__maria_graph = maria_graph

    async def get_maria_answer(self, user: UserModel, user_input: str) -> str:
        current_thread = await self.__get_current_thread(user.id)
        thread_id_str = str(current_thread.id)
        config = {"configurable": {"thread_id": thread_id_str}}
        user_input_with_name = f"{user.name}: {user_input}"

        async with self.__checkpointer as checkpointer:
            await checkpointer.setup()
            user_notion_databases = await self.__user_domain.get_user_notion_databases_taged(user.id)
            state_graph = await self.__maria_graph.get_state_graph(user.notion_authorization.access_token, user_notion_databases)
            compiled = state_graph.compile(checkpointer=checkpointer)
            result = await compiled.ainvoke({"user_input": HumanMessage(user_input_with_name)}, config=config, debug=True)
            messages = result["messages"]

        resp = messages[-1].content
        return resp
    
    async def __get_current_thread(self, user_id: str) -> ThreadModel:
        user_threads = await self.__user_domain.get_user_valid_thread(user_id)
        if len(user_threads) < 1:
            current_thread = await self.__user_domain.create_new_user_thread(user_id) 
        else:
            current_thread = user_threads[0]
        return current_thread