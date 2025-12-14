from notion_client import AsyncClient

from repository.db_models.notion_datasource_model import NotionDatasourceModel
from .notion_base_access.notion_external import NotionExternal
from .notion_base_access import EjFinanceAccess, SimpleFinanceAccess, BaseTemplateAccessInterface
from .notion_user.notion_tool import NotionTool
from .notion_user.notion_user_data import NotionUserData
from .notion_user.notion_authorization_data import NotionAuthorizationData

class NotionFactory:
    def __init__(self):
        self.__user_datasources: list[NotionDatasourceModel] = []
        self.__access_token = None
        self.__notion_client = None
        self.__notion_external = None
        self.__template_access = None
        self.__default_template = True

        self.__notion_authorization_data: NotionAuthorizationData = None
        self.__notion_tool: NotionTool = None
        self.__notion_user_data: NotionUserData = None

    def set_user_access_token(self, access_token:str):
        self.__access_token = access_token

    def set_user_datasources(self, notion_user_datasources: list[NotionDatasourceModel], use_default_template: bool = True):
        self.__user_datasources = notion_user_datasources
        self.__default_template = use_default_template

    def create_notion_tool(self) -> NotionTool:
        if self.__notion_tool != None:
            return self.__notion_tool
        
        self.__create_base_classes()
        
        self.__notion_tool = NotionTool(self.__template_access)
        return self.__notion_tool
    
    def create_notion_user_data(self) -> NotionUserData:
        if self.__notion_user_data != None:
            return self.__notion_user_data
        
        self.__create_base_classes()

        self.__notion_user_data = NotionUserData(self.__template_access)
        return self.__notion_user_data
    
    def create_notion_authorization_data(self) -> NotionAuthorizationData:
        self.__create_access_classes()
        self.__notion_authorization_data = NotionAuthorizationData(self.__notion_external)
        return self.__notion_authorization_data
    
    def __create_base_classes(self):
        self.__create_access_classes()
        
        if self.__template_access == None:
            self.__template_access = (
                SimpleFinanceAccess(self.__notion_external, self.__user_datasources)
                if self.__default_template
                else EjFinanceAccess(self.__notion_external, self.__user_datasources)
            )

    def __create_access_classes(self):
        if self.__notion_client == None:
            self.__notion_client = AsyncClient(
                auth=self.__access_token,
                notion_version = "2025-09-03"
            )

        if self.__notion_external == None:
            self.__notion_external = NotionExternal(self.__notion_client)
