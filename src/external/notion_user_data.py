from external.enum import NotionDatabaseEnum, UserDataTypes
from external import NotionAccess


class UserData:
    cards: dict
    categories: dict
    macroCategories: dict
    months: dict
    is_loaded: bool

# TODO algum lugar nao esta instanciando corretametne aqui
class NotionUserData:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NotionUserData, cls).__new__(cls)
        return cls._instance

    def __init__(self, notion_access: NotionAccess):
        if self.__class__._initialized:
            return
        if notion_access == None:
            raise Exception("Invalid notion_access")
        self.notion_access = notion_access
        self.user_data = UserData()
        self.user_data.is_loaded = False
        self.__class__._initialized = True

    async def get_user_base_data(self) -> UserData:
        if self.user_data.is_loaded:
            return self.user_data

        self.user_data.cards = self.notion_access.get_simple_data(NotionDatabaseEnum.CARDS)
        self.user_data.categories = self.notion_access.get_simple_data(NotionDatabaseEnum.CATEGORIES)
        self.user_data.macroCategories = self.notion_access.get_simple_data(NotionDatabaseEnum.MACRO_CATEGORIES)
        self.user_data.months = self.notion_access.get_simple_data(NotionDatabaseEnum.MONTHS)

        self.user_data.is_loaded = True

        return self.user_data
    
    async def get_data_id(self, data_type: UserDataTypes, register_name: str):
        if not self.user_data.is_loaded:
            await self.get_user_base_data()

        data = None
        user_data = getattr(self.user_data, data_type.value)
        for register in user_data['data']:
            if register['Name'] == register_name:
                data = register

        if data != None:
            return data['id']
        
        return None
    

