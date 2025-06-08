from application import MessageApplication
from fastapi import Depends
from collections.abc import Callable
from .custom_state import CustomState
from collections.abc import AsyncGenerator
from MARiA.tools import (
    CreateCard,
    CreateNewIncome,
    CreateNewMonth,
    CreateNewPlanning,
    CreateNewOutTransactionV2,
    CreateNewTransfer,
    SearchTransactionV2,
    ReadUserBaseData,
    GetPlanByMonth,
    DeleteData
)
from MARiA.agents import AgentBase, prompt_main_agent
from MARiA.notion_repository import notion_user_data
from MARiA import MariaGraph, get_checkpointer_manager, MariaInteraction
from langgraph.graph.state import CompiledStateGraph
from repository import UserRepository
from domain import UserDomain
from messaging import MessageService

def create_message_service() -> Callable[[], MessageService]:
    instance = 'maria'
    def dependency():
        return MessageService(instance)
    return dependency

def create_agente_base() -> AgentBase:
    tools = [
        CreateNewTransfer,
        CreateNewOutTransactionV2,
        CreateNewIncome,
        SearchTransactionV2,
        CreateCard,
        CreateNewMonth,
        CreateNewPlanning,
        GetPlanByMonth,
        DeleteData,
        ReadUserBaseData,
    ]
    agent = AgentBase(
        prompt=prompt_main_agent,
        notion_user_data=notion_user_data,
        ready_tools=[],
        tools=tools,
    )
    return agent

async def create_maria_graph() -> AsyncGenerator[CompiledStateGraph, None]:
    agent = create_agente_base()
    maria_graph = MariaGraph(agent)
    checkpointer_manager = get_checkpointer_manager()

    async with checkpointer_manager as checkpointer:
        await checkpointer.setup()

        graph_builder = await maria_graph.build_graph()
        compiled = graph_builder.compile(checkpointer=checkpointer)
        yield compiled

def create_user_repository(appState: CustomState) -> Callable[[], UserRepository]:
    def dependency():
        return UserRepository(appState.database)
    return dependency

def create_user_domain(appState: CustomState) -> Callable[[], UserDomain]:
    def dependency(
        repo = Depends(create_user_repository(appState))
    ):
        return UserDomain(repo)
    return dependency

def create_maria_interaction(appState: CustomState) -> Callable[[], MariaInteraction]:
    async def dependency(
        maria_graph: CompiledStateGraph = Depends(create_maria_graph),
        user_domain: UserDomain = Depends(create_user_domain(appState)),
    ):
        return MariaInteraction(maria_graph, user_domain)
    return dependency


def create_message_application(appState: CustomState) -> Callable[[], MessageApplication]:
    async def dependency(
            user_domain = Depends(create_user_domain(appState)),
            maria_interaction = Depends(create_maria_interaction(appState)),
            message_service = Depends(create_message_service())
    ) -> MessageApplication:
        return MessageApplication(user_domain, maria_interaction, message_service)

    return dependency
