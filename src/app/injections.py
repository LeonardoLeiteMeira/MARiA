from collections.abc import Callable

from fastapi import Depends

from application import (
    MessageApplication,
    NotionAuthorizationApplication,
    AuthApplication,
    OpenFinanceApplication,
    ManagementPeriodApplication,
    CategoryApplication,
    ManagementPlanningApplication,
    AccountApplication,
    TransactionApplication,
    UserApplication
)
from domain import (
    UserDomain,
    NotionAuthorizationDomain,
    PluggyItemDomain,
    AuthDomain,
    ManagementPeriodDomain,
    CategoryDomain,
    MacroCategoryDomain,
    ManagementPlanningDomain,
    AccountDomain,
    TransactionDomain,
    RecoverPasswordDomain,
)
from MARiA import MariaGraph, MariaInteraction, get_checkpointer_manager
from MARiA import AgentBase, prompt_main_agent
from MARiA.tools import (CreateCard, CreateNewIncome, CreateNewMonth,
                         CreateNewOutTransactionV2, CreateNewPlanning,
                         CreateNewTransfer, DeleteData, GetPlanByMonth,
                         ReadUserBaseData, SearchTransactionV2, GetMonthData, RedirectTransactionsAgent)
from external.whatsapp import MessageService, MessageServiceDev
from repository import (
    UserRepository,
    NotionAuthorizationRepository,
    NotionDatabaseRepository,
    AuthRepository,
    PluggyItemRepository,
    ManagementPeriodRepository,
    CategoryRepository,
    MacroCategoryRepository,
    ManagementPlanningRepository,
    AccountRepository,
    TransactionRepository,
    RecoverPasswordRepository,
)
from external.notion import NotionFactory
from external.pluggy import PluggyAuthLoader
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
    def dependency():
        tools = [
            #Tools do transaction agent
            SearchTransactionV2,
            CreateNewIncome,
            CreateNewOutTransactionV2,
            CreateNewTransfer,
            #=====

            CreateCard,
            CreateNewMonth,
            CreateNewPlanning,
            GetPlanByMonth,
            DeleteData,
            ReadUserBaseData,
            GetMonthData,
            # RedirectTransactionsAgent
        ]
        agent = AgentBase(
            tools=tools
        )
        return agent
    return dependency

def create_maria_graph() -> Callable[[], MariaGraph]:
    def dependency(agent_base = Depends(create_agente_base()), notion_factory = Depends(create_notion_factory())):
        return MariaGraph(agent_base, prompt_main_agent, notion_factory)
    return dependency


def create_user_repository(appState: CustomState) -> Callable[[], UserRepository]:
    def dependency():
        return UserRepository(appState.database)
    return dependency

def create_pluggy_item_repository(appState: CustomState) -> Callable[[], PluggyItemRepository]:
    def dependency():
        return PluggyItemRepository(appState.database)
    return dependency

def create_notion_database_repository(appState: CustomState) -> Callable[[], UserDomain]:
    def dependency():
        return NotionDatabaseRepository(appState.database)
    return dependency

def create_user_domain(appState: CustomState) -> Callable[[], UserDomain]:
    def dependency(
        repo=Depends(create_user_repository(appState)),
        notion_db_repo=Depends(create_notion_database_repository(appState))
    ):
        return UserDomain(repo, notion_db_repo)

    return dependency

def create_pluggy_item_domain(appState: CustomState):
    def dep(repo=Depends(create_pluggy_item_repository(appState)),):
        return PluggyItemDomain(repo)
    return dep

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

def create_open_finance_application(appState: CustomState) -> Callable[[], OpenFinanceApplication]:
    def dep(
        pluggy_item_domain=Depends(create_pluggy_item_domain(appState)),
        pluggy_auth_loader=Depends(create_pluggy_auth_loader()),
    ):
        return OpenFinanceApplication(pluggy_item_domain, pluggy_auth_loader)

    return dep

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
        user_domain=Depends(create_user_domain(appState)),
        notion_factory=Depends(create_notion_factory())
    ) -> NotionAuthorizationApplication:
        return NotionAuthorizationApplication(domain, user_domain, notion_factory)

    return dependency


# ===== Management Period dependencies =====================================
def create_management_period_repository(appState: CustomState) -> Callable[[], ManagementPeriodRepository]:
    def dependency():
        return ManagementPeriodRepository(appState.database)
    return dependency


def create_management_period_domain(appState: CustomState) -> Callable[[], ManagementPeriodDomain]:
    def dependency(repo=Depends(create_management_period_repository(appState))):
        return ManagementPeriodDomain(repo)
    return dependency


def create_management_period_application(appState: CustomState) -> Callable[[], ManagementPeriodApplication]:
    def dependency(
            domain=Depends(create_management_period_domain(appState)),
            plan_domain=Depends(create_management_planning_domain(appState)),
            category_domain=Depends(create_category_domain(appState)),
            macro_category_domain=Depends(create_macro_category_domain(appState)),
            transaction_domain=Depends(create_transaction_domain(appState)),
        ) -> ManagementPeriodApplication:
        return ManagementPeriodApplication(domain, plan_domain, category_domain, macro_category_domain,transaction_domain)
    return dependency


# ===== Category & Macro Category dependencies ==============================
def create_category_repository(appState: CustomState) -> Callable[[], CategoryRepository]:
    def dependency():
        return CategoryRepository(appState.database)
    return dependency


def create_macro_category_repository(appState: CustomState) -> Callable[[], MacroCategoryRepository]:
    def dependency():
        return MacroCategoryRepository(appState.database)
    return dependency


def create_category_domain(appState: CustomState) -> Callable[[], CategoryDomain]:
    def dependency(repo=Depends(create_category_repository(appState))):
        return CategoryDomain(repo)
    return dependency


def create_macro_category_domain(appState: CustomState) -> Callable[[], MacroCategoryDomain]:
    def dependency(repo=Depends(create_macro_category_repository(appState))):
        return MacroCategoryDomain(repo)
    return dependency


def create_category_application(appState: CustomState) -> Callable[[], CategoryApplication]:
    def dependency(
        category_domain=Depends(create_category_domain(appState)),
        macro_domain=Depends(create_macro_category_domain(appState)),
    ) -> CategoryApplication:
        return CategoryApplication(category_domain, macro_domain)

    return dependency


# ===== Management Planning dependencies ====================================
def create_management_planning_repository(appState: CustomState) -> Callable[[], ManagementPlanningRepository]:
    def dependency():
        return ManagementPlanningRepository(appState.database)
    return dependency


def create_management_planning_domain(appState: CustomState) -> Callable[[], ManagementPlanningDomain]:
    def dependency(repo=Depends(create_management_planning_repository(appState))):
        return ManagementPlanningDomain(repo)
    return dependency


def create_management_planning_application(appState: CustomState) -> Callable[[], ManagementPlanningApplication]:
    def dependency(domain=Depends(create_management_planning_domain(appState))) -> ManagementPlanningApplication:
        return ManagementPlanningApplication(domain)
    return dependency


# ===== Account dependencies =================================================
def create_account_repository(appState: CustomState) -> Callable[[], AccountRepository]:
    def dependency():
        return AccountRepository(appState.database)
    return dependency


def create_account_domain(appState: CustomState) -> Callable[[], AccountDomain]:
    def dependency(repo=Depends(create_account_repository(appState))):
        return AccountDomain(repo)
    return dependency


def create_account_application(appState: CustomState) -> Callable[[], AccountApplication]:
    def dependency(
            domain=Depends(create_account_domain(appState)),
            transaction_domain=Depends(create_transaction_domain(appState))
        ) -> AccountApplication:
        return AccountApplication(domain, transaction_domain)
    return dependency


# ===== Transaction dependencies ===========================================
def create_transaction_repository(appState: CustomState) -> Callable[[], TransactionRepository]:
    def dependency():
        return TransactionRepository(appState.database)
    return dependency


def create_transaction_domain(appState: CustomState) -> Callable[[], TransactionDomain]:
    def dependency(repo=Depends(create_transaction_repository(appState))):
        return TransactionDomain(repo)
    return dependency


def create_transaction_application(appState: CustomState) -> Callable[[], TransactionApplication]:
    def dependency(domain=Depends(create_transaction_domain(appState))) -> TransactionApplication:
        return TransactionApplication(domain)
    return dependency


def create_recover_password_repository(appState: CustomState) -> Callable[[], RecoverPasswordRepository]:
    def dependency():
        return RecoverPasswordRepository(appState.database)
    return dependency


def create_recover_password_domain(appState: CustomState) -> Callable[[], RecoverPasswordDomain]:
    def dependency(repo=Depends(create_recover_password_repository(appState))):
        return RecoverPasswordDomain(repo)
    return dependency


def create_auth_repository(appState: CustomState) -> Callable[[], AuthRepository]:
    def dependency():
        return AuthRepository(appState.database)

    return dependency


def create_auth_domain(appState: CustomState) -> Callable[[], AuthDomain]:
    def dependency(repo=Depends(create_auth_repository(appState))):
        return AuthDomain(repo)

    return dependency


def create_auth_application(appState: CustomState) -> Callable[[], AuthApplication]:
    def dependency(
        domain=Depends(create_auth_domain(appState)),
        message_service=Depends(create_message_service()),
        recover_password_domain=Depends(create_recover_password_domain(appState)),
    ) -> AuthApplication:
        return AuthApplication(domain, message_service, recover_password_domain)

    return dependency

def create_pluggy_auth_loader() ->  Callable[[], PluggyAuthLoader]:
    def dependency() -> PluggyAuthLoader:
        return PluggyAuthLoader(settings)
    
    return dependency

def create_user_application(appState: CustomState) -> Callable[[], UserApplication]:
    def dependency(
            user_domain=Depends(create_user_domain(appState)),
            category_domain=Depends(create_category_domain(appState))
        ) -> UserApplication:
        return UserApplication(user_domain, category_domain)
    
    return dependency
