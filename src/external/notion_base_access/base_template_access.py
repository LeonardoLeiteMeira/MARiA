from abc import ABC
import urllib.parse

from repository.db_models.notion_database_model import NotionDatabaseModel
from .notion_external import NotionExternal
from ..enum import NotionDatabaseEnum, TransactionType


class BaseTemplateAccessInterface(ABC):
    def __init__(self, notion_external: NotionExternal, user_databases: list[NotionDatabaseModel]):
        self.notion_external = notion_external
        self.databases = {
            user_db.tag: {
                'id': user_db.table_id
            }
            for user_db in user_databases
        }
        self.cache = {}
    
    def __get_properties(self, database: NotionDatabaseEnum) -> dict:
        if 'properties' in self.databases[database.value]:
            return self.databases[database.value]['properties']
        
        database_id = self.databases[database.value]['id']
        data = self.notion_external.retrieve_databse(database_id)
        self.databases[database.value]['properties'] = data['properties']
        return self.databases[database.value]['properties']
    
    def get_full_categories(self) -> dict:
        '''It's lazy because load a lot of data'''
        data = self.notion_external.get_database(self.databases[NotionDatabaseEnum.CATEGORIES.value]['id'])
        return self.notion_external.process_database_registers(data)
    
    def get_simple_data(self, database: NotionDatabaseEnum, cursor: str = None, property_ids: list[str] = []):
        full_properties = self.__get_properties(database)
        title_property_id = self.__get_title_property_from_schema(full_properties)
        property_ids_parsed = [urllib.parse.unquote(id) for id in property_ids]
        data = self.notion_external.get_database(
            self.databases[database.value]['id'], 
            filter_properties=[title_property_id, *property_ids_parsed],
            start_cursor=cursor
        )
        return self.notion_external.process_database_registers(data)
    
    def get_properties(self, database: str) -> dict:
        full_properties = self.__get_properties(database)
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
    
    def get_page_by_id(self, month_id, exclude_properties: list[str] = []):
        data = self.notion_external.get_page(month_id)
        for prop in exclude_properties:
            data['properties'].pop(prop, None)
        return self.notion_external.process_page_register(data)
    
    def delete_page(self, page_id: str):
        self.notion_external.delete_page(page_id)

    def __get_title_property_from_schema(self, schema:dict) -> str:
        for key, value in schema.items():
            if value['type'] == 'title':
                return value['id']
        return None