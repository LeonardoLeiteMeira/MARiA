from notion_client import Client
from .notion_external import NotionExternal
from .notion_access import NotionAccess
from .notion_tool import NotionTool
from .notion_user_data import NotionUserData

class NotionFactory:
    def __init__(self):
        self.__access_token = None
        self.__notion_client = None
        self.__notion_external = None
        self.__notion_access = None

        self.__notion_tool = None
        self.__notion_user_data = None

    def set_user_access_token(self, access_token:str):
        self.__access_token = access_token

    def create_notion_tool(self):
        if self.__notion_tool != None:
            return self.__notion_tool
        
        self.__create_base_classes()
        
        self.__notion_tool = NotionTool(self.__notion_access)
        return self.__notion_tool
    
    def create_notion_user_data(self):
        if self.__notion_user_data != None:
            return self.__notion_user_data
        
        self.__create_base_classes()

        self.__notion_user_data = NotionUserData(self.__notion_access)
        return self.__notion_user_data
    
    def __create_base_classes(self):
        if self.__notion_client == None:
            self.__notion_client = Client(auth=self.__access_token)

        if self.__notion_external == None:
            self.__notion_external = NotionExternal(self.__notion_client)
        
        if self.__notion_access == None: 
            self.__notion_access = NotionAccess(self.__notion_external)
