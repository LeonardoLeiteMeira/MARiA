from abc import ABC, abstractmethod
import urllib.parse

from repository.db_models.notion_datasource_model import NotionDatasourceModel
from .notion_external import NotionExternal
from ..enum import NotionDatasourceEnum, TemplateTypes


class BaseTemplateAccessInterface(ABC):
    def __init__(self, notion_external: NotionExternal, user_datasources: list[NotionDatasourceModel]):
        self.notion_external = notion_external
        self.datasources = {
            user_datasource.tag: {
                'id': user_datasource.table_id
            }
            for user_datasource in user_datasources
        }
        self.cache = {}

    @abstractmethod
    async def get_transactions(self, cursor: str = None, page_size: int = None, filter: dict = None, properties: list = None) -> dict:
        pass

    @abstractmethod
    async def new_get_transactions(
        self,
        name: str|None,
        has_paid: bool|None,
        card_account_enter_id: str|None,
        card_account_out_id: str|None,
        category_id: str|None,
        macro_category_id: str|None,
        month_id: str|None,
        transaction_type: str|None,
        cursor: str| None,
        page_size: int
    ) -> dict:
        pass

    @abstractmethod
    def get_transaction_enum(self):
        pass

    @abstractmethod
    async def get_months_by_year(self, year:int|None, property_ids: list[str] = []) -> dict:
        pass

    @abstractmethod
    async def get_current_month(self) -> dict:
        pass
    
    @abstractmethod
    async def create_out_transaction(self, name: str, month_id:str, amount: float, date:str, card_id:str, category_id:str, type_id:str, status: bool = True):
        pass

    @abstractmethod
    async def create_in_transaction(self, name:str, month_id:str, amount:float, date:str, card_id:str, status: bool = True):
        pass

    @abstractmethod
    async def create_transfer_transaction(self, name:str, month_id:str, amount:str, date:str, account_id_in:str, account_id_out:str, status: bool = True):
        pass
    
    @abstractmethod
    async def create_planning(
        self,
        name,
        month_id,
        category_id,
        amount,
        text 
    ):
        pass

    @abstractmethod
    async def create_card(self, name: str, initial_balance: float):
        pass

    @abstractmethod
    async def create_month(self, name: str, start_date:str, finish_date:str):
        pass

    @abstractmethod
    async def get_planning_by_month(self, month_id) -> dict:
        pass
    
    async def __get_properties(self, datasource: NotionDatasourceEnum) -> dict:
        if 'properties' in self.datasources[datasource.value]:
            return self.datasources[datasource.value]['properties']

        datasource_id = self.datasources[datasource.value]['id']
        data = await self.notion_external.retrieve_datasource(datasource_id)
        self.datasources[datasource.value]['properties'] = data['properties']
        return self.datasources[datasource.value]['properties']

    async def get_full_categories(self) -> dict:
        '''It's lazy because load a lot of data'''
        data = await self.notion_external.get_datasource(self.datasources[NotionDatasourceEnum.CATEGORIES.value]['id'])
        return await self.notion_external.process_datasource_registers(data)

    async def get_simple_data(self, datasource: NotionDatasourceEnum, cursor: str = None, property_ids: list[str] = [], template_type: TemplateTypes = None):
        full_properties = await self.__get_properties(datasource)
        title_property_id = self.__get_title_property_from_schema(full_properties)
        property_ids_parsed = [urllib.parse.unquote(id) for id in property_ids]

        sort = self.__get_sort(datasource, template_type)

        data = await self.notion_external.get_datasource(
            self.datasources[datasource.value]['id'],
            filter_properties=[title_property_id, *property_ids_parsed],
            start_cursor=cursor,
            sorts=sort
        )
        return await self.notion_external.process_datasource_registers(data)

    async def get_properties(self, datasource: NotionDatasourceEnum) -> dict:
        full_properties = await self.__get_properties(datasource)
        properties = {}
        for key, value in full_properties.items():
            properties[key] = {
                "id":value["id"],
                "name":value["name"],
                "type":value["type"],
                "description":value.get("description", ""),
                value["type"]: value.get(value["type"], None)
            }   
        return properties

    async def get_page_by_id(self, month_id, exclude_properties: list[str] = []):
        data = await self.notion_external.get_page(month_id)
        for prop in exclude_properties:
            data['properties'].pop(prop, None)
        return await self.notion_external.process_page_register(data)

    async def delete_page(self, page_id: str):
        await self.notion_external.delete_page(page_id)

    def __get_title_property_from_schema(self, schema:dict) -> str:
        for key, value in schema.items():
            if value['type'] == 'title':
                return value['id']
        return None
    
    def __get_sort(self, datasource: NotionDatasourceEnum, template_type: TemplateTypes | None) -> list:
        if template_type is None:
            return []

        if datasource == NotionDatasourceEnum.MONTHS:
            if template_type is TemplateTypes.EJ_FINANCE_TEMPLATE:
                return [{
                    "property": "Data Fim",
                    "direction": "descending"
                }]

            if template_type is TemplateTypes.SIMPLE_TEMPLATE:
                return [{
                    "property": "MesData",
                    "direction": "descending"
                }]

        return []
