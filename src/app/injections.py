from collections.abc import AsyncGenerator, Callable

from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph
from notion_client import Client

from application import MessageApplication, NotionAuthorizationApplication
from domain import UserDomain, NotionAuthorizationDomain
from MARiA import MariaGraph, MariaInteraction, get_checkpointer_manager
from MARiA.agents import AgentBase, prompt_main_agent
from MARiA.tools import (CreateCard, CreateNewIncome, CreateNewMonth,
                         CreateNewOutTransactionV2, CreateNewPlanning,
                         CreateNewTransfer, DeleteData, GetPlanByMonth,
                         ReadUserBaseData, SearchTransactionV2)
from messaging import MessageService, MessageServiceDev
from repository import UserRepository, NotionAuthorizationRepository
from external import NotionFactory
from config import get_settings

from .custom_state import CustomState

settings = get_settings()

def create_notion_factory() -> Callable[[], NotionFactory]: 
    def dependency():
        return NotionFactory()
    return dependency

def create_message_service() -> Callable[[], MessageService]:
    def dependency():
        instance = "maria"
        if settings.is_production:
            return MessageService(instance)
        else:
            return MessageServiceDev(instance)
    return dependency


def create_agente_base() -> Callable[[], AgentBase]:
    def dependency(
        notion_factory = Depends(create_notion_factory())
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
            tools=tools,
            notion_factory=notion_factory
        )
        return agent
    return dependency

def create_maria_graph() -> Callable[[], MariaGraph]:
    def dependency(agent_base = Depends(create_agente_base())):
        return MariaGraph(agent_base)
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
        maria_graph = Depends(create_maria_graph()),
        user_domain: UserDomain = Depends(create_user_domain(appState)),
        checkpoint_manager = Depends(get_checkpointer_manager)
    ):
        return MariaInteraction(user_domain, maria_graph, checkpoint_manager)

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
