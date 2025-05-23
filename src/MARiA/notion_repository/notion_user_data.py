from enum import Enum
from MARiA.notion_types import NotionDatabaseEnum
from .notion_access import NotionAccess


class UserDataTypes(Enum):
    MONTHS = 'months'
    CATEGORIES = 'categories'
    MACRO_CATEGORIES = 'macroCategories'
    CARDS = 'cards'

class UserData:
    cards: dict
    categories: dict
    macroCategories: dict
    months: dict
    is_loaded: bool


class NotionUserData:
    def __init__(self, notion_access: NotionAccess):
        self.notion_access = notion_access
        self.user_data = UserData()
        self.user_data.is_loaded = False

    async def getUserBaseData(self) -> UserData:
        if self.user_data.is_loaded:
            return self.user_data

        self.user_data.cards = self.notion_access.get_simple_data(NotionDatabaseEnum.CARDS)
        self.user_data.categories = self.notion_access.get_simple_data(NotionDatabaseEnum.CATEGORIES)
        self.user_data.macroCategories = self.notion_access.get_simple_data(NotionDatabaseEnum.TYPES)
        self.user_data.months = self.notion_access.get_simple_data(NotionDatabaseEnum.MONTHS)

        self.user_data.is_loaded = True

        return self.user_data
    
    async def get_data_id(self, data_type: UserDataTypes, register_name: str):
        if not self.user_data.is_loaded:
            await self.getUserBaseData()

        data = None
        user_data = getattr(self.user_data, data_type.value)
        for register in user_data['data']:
            if register['Name'] == register_name:
                data = register

        if data != None:
            return data['id']
        
        return None
    

