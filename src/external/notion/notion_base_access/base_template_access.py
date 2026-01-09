from abc import ABC, abstractmethod
import urllib.parse
from typing import Any, cast

from repository.db_models.notion_datasource_model import NotionDatasourceModel
from .notion_external import NotionExternal
from ..enum import NotionDatasourceEnum, TemplateTypes, GlobalTransactionType
from enum import Enum


class BaseTemplateAccessInterface(ABC):
    def __init__(self, notion_external: NotionExternal, user_datasources: list[NotionDatasourceModel]) -> None:
        self.notion_external = notion_external
        self.datasources: dict[str, dict[str, Any]] = {
            user_datasource.tag: {
                'id': user_datasource.table_id
            }
            for user_datasource in user_datasources
        }
        self.cache: dict[str, Any] = {}

    @abstractmethod
    async def get_transactions(
        self,
        cursor: str | None = None,
        page_size: int | None = None,
        filter: dict[str, Any] | None = None,
        properties: list[Any] | None = None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def new_get_transactions(
        self,
        name: str | None,
        has_paid: bool | None,
        card_account_enter_id: str | None,
        card_account_out_id: str | None,
        category_id: str | None,
        macro_category_id: str | None,
        month_id: str | None,
        transaction_type: str | None,
        cursor: str | None,
        page_size: int | None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_transaction_enum(self) -> type[Enum]:
        pass

    @abstractmethod
    async def get_months_by_year(self, year: int | None, property_ids: list[str] = []) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_current_month(self) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def create_out_transaction(
        self,
        name: str,
        month_id: str,
        amount: Any,
        date: str,
        card_id: str,
        category_id: str | None,
        macro_category_id: str | None,
        status: bool = True,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def create_in_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        card_id: str,
        status: bool = True,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def create_transfer_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        account_id_in: str,
        account_id_out: str,
        status: bool = True,
    ) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def create_planning(
        self,
        name: str,
        month_id: str,
        category_id: str,
        amount: float,
        text: str,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def create_card(self, name: str, initial_balance: float) -> dict[str, Any]:
        pass

    @abstractmethod
    async def create_month(self, name: str, start_date: str, finish_date: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_planning_by_month(self, month_id: str) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_accounts_with_balance(self) -> dict[str, Any]:
        pass
    
    @abstractmethod
    async def create_new_transaction(
            self,
            name: str,
            month_id: str,
            amount: float,
            date: str,
            transaction_type: GlobalTransactionType,
            enter_account_id: str | None = None,
            debit_account_id: str | None = None,
            category_id: str | None = None,
            macro_category_id: str | None = None,
            status: bool = True,
        ) -> dict[str, Any]:
        pass
    
    async def __get_properties(self, datasource: NotionDatasourceEnum) -> dict[str, Any]:
        if 'properties' in self.datasources[datasource.value]:
            return cast(dict[str, Any], self.datasources[datasource.value]['properties'])

        datasource_id = self.datasources[datasource.value]['id']
        data = await self.notion_external.retrieve_datasource(datasource_id)
        self.datasources[datasource.value]['properties'] = data['properties']
        return cast(dict[str, Any], self.datasources[datasource.value]['properties'])

    async def get_full_categories(self) -> dict[str, Any]:
        '''It's lazy because load a lot of data'''
        data = await self.notion_external.get_datasource(self.datasources[NotionDatasourceEnum.CATEGORIES.value]['id'])
        processed = await self.notion_external.process_datasource_registers(data)
        return processed

    async def get_simple_data(
        self,
        datasource: NotionDatasourceEnum,
        cursor: str | None = None,
        property_ids: list[str] = [],
        template_type: TemplateTypes | None = None,
    ) -> dict[str, Any]:
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
        processed = await self.notion_external.process_datasource_registers(data)
        return processed

    async def get_properties(self, datasource: NotionDatasourceEnum) -> dict[str, Any]:
        full_properties = await self.__get_properties(datasource)
        properties: dict[str, Any] = {}
        for key, value in full_properties.items():
            properties[key] = {
                "id":value["id"],
                "name":value["name"],
                "type":value["type"],
                "description":value.get("description", ""),
                value["type"]: value.get(value["type"], None)
            }   
        return properties

    async def get_page_by_id(self, month_id: str, exclude_properties: list[str] = []) -> dict[str, Any]:
        data = await self.notion_external.get_page(month_id)
        for prop in exclude_properties:
            data['properties'].pop(prop, None)
        return await self.notion_external.process_page_register(data)

    async def delete_page(self, page_id: str) -> None:
        await self.notion_external.delete_page(page_id)

    async def get_property_id_from_datasource_by_property_name(self, datasource: NotionDatasourceEnum, property_name: str) -> str | None:
        full_properties = await self.__get_properties(datasource)
        for key, value in full_properties.items():
            if key == property_name:
                return cast(str, value['id'])
        return None

    def __get_title_property_from_schema(self, schema: dict[str, Any]) -> str | None:
        for key, value in schema.items():
            if value['type'] == 'title':
                return cast(str, value['id'])
        return None
    
    def __get_sort(
        self,
        datasource: NotionDatasourceEnum,
        template_type: TemplateTypes | None,
    ) -> list[dict[str, str]]:
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
