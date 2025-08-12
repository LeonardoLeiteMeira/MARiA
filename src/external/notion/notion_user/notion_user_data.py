from ..enum import NotionDatabaseEnum, UserDataTypes
from .. import BaseTemplateAccessInterface


class UserData:
    cards: dict = None
    categories: dict = None
    macroCategories: dict = None
    months: dict = None
    is_loaded: bool = None

class NotionUserData:
    def __init__(self, template_access: BaseTemplateAccessInterface):
        self.template_access = template_access
        self.user_data = UserData()
        self.user_data.is_loaded = False
        self.__class__._initialized = True

    #TODO remover para ter um metodo para cada dado
    async def get_user_base_data(self) -> UserData:
        if self.user_data.is_loaded:
            return self.user_data

        self.user_data.cards = await self.template_access.get_simple_data(NotionDatabaseEnum.CARDS)
        self.user_data.categories = await self.template_access.get_simple_data(NotionDatabaseEnum.CATEGORIES)
        self.user_data.macroCategories = await self.template_access.get_simple_data(NotionDatabaseEnum.MACRO_CATEGORIES)
        self.user_data.months = await self.template_access.get_simple_data(NotionDatabaseEnum.MONTHS)

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
    
    async def get_user_cards(self):
        if getattr(self.user_data, 'cards', None):
            return self.user_data.cards
        self.user_data.cards = await self.template_access.get_simple_data(NotionDatabaseEnum.CARDS)
        return self.user_data.cards

    async def get_user_categories(self):
        if getattr(self.user_data, 'categories', None):
            return self.user_data.categories
        self.user_data.categories = await self.template_access.get_simple_data(NotionDatabaseEnum.CATEGORIES)
        return self.user_data.categories

    async def get_user_macro_categories(self):
        if getattr(self.user_data, 'macroCategories', None):
            return self.user_data.macroCategories
        self.user_data.macroCategories = await self.template_access.get_simple_data(NotionDatabaseEnum.MACRO_CATEGORIES)
        return self.user_data.macroCategories

    async def get_user_months(self):
        if getattr(self.user_data, 'months', None):
            return self.user_data.months
        self.user_data.months = await self.template_access.get_simple_data(NotionDatabaseEnum.MONTHS)
        return self.user_data.months
