from notion_client import Client

from repository.db_models.notion_database_model import NotionDatabaseModel
from .notion_base_access.notion_external import NotionExternal
from .notion_base_access.ej_finance_access import EjFinanceAccess
from .notion_user.notion_tool import NotionTool
from .notion_user.notion_user_data import NotionUserData
from .notion_user.notion_authorization_data import NotionAuthorizationData

class NotionFactory:
    def __init__(self):
        self.__user_databases: list[NotionDatabaseModel] = []
        self.__access_token = None
        self.__notion_client = None
        self.__notion_external = None
        self.__ej_finance_access = None

        self.__notion_authorization_data: NotionAuthorizationData = None
        self.__notion_tool: NotionTool = None
        self.__notion_user_data: NotionUserData = None

    def set_user_access_token(self, access_token:str):
        self.__access_token = access_token

    def set_user_databases(self, notion_user_databases: list[NotionDatabaseModel]):
        self.__user_databases = notion_user_databases

    def create_notion_tool(self) -> NotionTool:
        if self.__notion_tool != None:
            return self.__notion_tool
        
        self.__create_base_classes()
        
        self.__notion_tool = NotionTool(self.__ej_finance_access)
        return self.__notion_tool
    
    def create_notion_user_data(self) -> NotionUserData:
        if self.__notion_user_data != None:
            return self.__notion_user_data
        
        self.__create_base_classes()

        self.__notion_user_data = NotionUserData(self.__ej_finance_access)
        return self.__notion_user_data
    
    def create_notion_authorization_data(self) -> NotionAuthorizationData:
        self.__create_access_classes()
        self.__notion_authorization_data = NotionAuthorizationData(self.__notion_external)
        return self.__notion_authorization_data
    
    def __create_base_classes(self):
        self.__create_access_classes()
        
        if self.__ej_finance_access == None: 
            self.__ej_finance_access = EjFinanceAccess(self.__notion_external, self.__user_databases)

    def __create_access_classes(self):
        if self.__notion_client == None:
            self.__notion_client = Client(auth=self.__access_token)

        if self.__notion_external == None:
            self.__notion_external = NotionExternal(self.__notion_client)
