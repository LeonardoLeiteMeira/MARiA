from collections.abc import AsyncGenerator, Callable

from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph
from notion_client import Client

from application import MessageApplication, NotionAuthorizationApplication
from domain import UserDomain, NotionAuthorizationDomain, NotionUserDataDomain, NotionToolDomain
from MARiA import MariaGraph, MariaInteraction, get_checkpointer_manager
from MARiA.agents import AgentBase, prompt_main_agent
from MARiA.tools import (CreateCard, CreateNewIncome, CreateNewMonth,
                         CreateNewOutTransactionV2, CreateNewPlanning,
                         CreateNewTransfer, DeleteData, GetPlanByMonth,
                         ReadUserBaseData, SearchTransactionV2)
from messaging import MessageService
from repository import UserRepository, NotionAuthorizationRepository
from external import NotionAccess, NotionExternal
from config import get_settings

from .custom_state import CustomState

settings = get_settings()

def create_notion_external() -> Callable[[], NotionExternal]:
    def dependency():
        api_key = settings.notion_api_key
        notion = Client(auth=api_key)
        return NotionExternal(notion)
    return dependency


def create_notion_access() -> Callable[[], NotionAccess]:
    def dependency(notion_external = Depends(create_notion_external())):
        return NotionAccess(notion_external)
    return dependency


def create_notion_user_data_domain() -> Callable[[], NotionUserDataDomain]:
    def dependency(notion_access = Depends(create_notion_access())):
        return NotionUserDataDomain(notion_access)
    return dependency

def create_notion_tool_domain() -> Callable[[], NotionToolDomain]:
    def dependency(notion_access = Depends(create_notion_access())):
        return NotionToolDomain(notion_access)
    return dependency

def create_message_service() -> Callable[[], MessageService]:
    def dependency():
        instance = "maria"
        return MessageService(instance)
    return dependency


def create_agente_base() -> Callable[[], AgentBase]:
    def dependency(
        notion_user_data = Depends(create_notion_user_data_domain()),
        notion_tool_domain = Depends(create_notion_tool_domain())
    ):
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
            notion_tool_domain=notion_tool_domain,
            tools=tools,
        )
        return agent
    return dependency


def create_maria_graph() ->  Callable[[], AsyncGenerator[CompiledStateGraph, None]]:
    async def dependency(agent = Depends(create_agente_base())) -> AsyncGenerator[CompiledStateGraph, None]:
        maria_graph = MariaGraph(agent)
        checkpointer_manager = get_checkpointer_manager()

        async with checkpointer_manager as checkpointer:
            await checkpointer.setup()

            graph_builder = await maria_graph.build_graph()
            compiled = graph_builder.compile(checkpointer=checkpointer)
            yield compiled
    return dependency


def create_user_repository(appState: CustomState) -> Callable[[], UserRepository]:
    def dependency():
        return UserRepository(appState.database)

    return dependency


def create_user_domain(appState: CustomState) -> Callable[[], UserDomain]:
    def dependency(repo=Depends(create_user_repository(appState))):
        return UserDomain(repo)

    return dependency


def create_maria_interaction(appState: CustomState) -> Callable[[], MariaInteraction]:
    async def dependency(
        maria_graph: CompiledStateGraph = Depends(create_maria_graph()),
        user_domain: UserDomain = Depends(create_user_domain(appState)),
    ):
        return MariaInteraction(maria_graph, user_domain)

    return dependency


def create_message_application(
    appState: CustomState,
) -> Callable[[], MessageApplication]:
    async def dependency(
        user_domain=Depends(create_user_domain(appState)),
        maria_interaction=Depends(create_maria_interaction(appState)),
        message_service=Depends(create_message_service()),
    ) -> MessageApplication:
        return MessageApplication(user_domain, maria_interaction, message_service)

    return dependency

def create_notion_authorization_repository(
    appState: CustomState,
) -> Callable[[], NotionAuthorizationRepository]:
    def dependency():
        return NotionAuthorizationRepository(appState.database)

    return dependency

def create_notion_authorization_domain(
    appState: CustomState,
) -> Callable[[], NotionAuthorizationDomain]:
    def dependency(repo=Depends(create_notion_authorization_repository(appState))):
        return NotionAuthorizationDomain(repo)

    return dependency


def create_notion_authorization_application(
    appState: CustomState,
) -> Callable[[], NotionAuthorizationApplication]:
    async def dependency(
        domain=Depends(create_notion_authorization_domain(appState)),
    ) -> NotionAuthorizationApplication:
        return NotionAuthorizationApplication(domain)

    return dependency
