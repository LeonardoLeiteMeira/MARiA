from MARiA.notion_types import NotionDatabaseEnum
from .notion_repository import NotionRepository
from .basic_property import BasicProperty
import urllib.parse

notion_cache = None

class NotionAccess:
    def __init__(self, notion_repository: NotionRepository):
        self.notion_repository = notion_repository
        self.databases = {
            NotionDatabaseEnum.TRANSACTIONS.value: {
                "id": "97c5aad2c46d46a49c3b78e83473ae52"
            },
            NotionDatabaseEnum.CATEGORIES.value : {
                "id": "38236d860412473fa9f8d3a0f1e4b0e1"
            },
            NotionDatabaseEnum.MONTHS.value : {
                "id": "d91b81e32555418a8bb62a76d7c69ac7"
            },
            NotionDatabaseEnum.CARDS.value: {
                "id" : "d1f6611fa1c046eb8cdf87ba3c757f6b"
            },
            NotionDatabaseEnum.TYPES.value: {
                'id': '6852342492704ecf8205c6ac953cf3a2'
            },
            NotionDatabaseEnum.PLANNING.value: {
                'id': 'e1bb24b27a5b41c6879b7ff51d18673c'
            }
        }
        self.cache = {}
        self.__load_database_schema()

    def __load_database_schema(self) -> dict:
        global notion_cache
        if notion_cache != None:
            for key, value in self.databases.items():
                value['properties'] = notion_cache[value['id']]

        notion_cache = {}
        for key, value in self.databases.items():
            data = self.notion_repository.retrieve_databse(value['id'])
            value['properties'] = data['properties']
            notion_cache[value['id']] = value['properties']

    def get_transactions(self, cursor: str = None, page_size: int = None, filter: dict = None, properties: list = None) -> dict:
        if properties!= None:
            properties = [urllib.parse.unquote(id) for id in properties]
        data = self.notion_repository.get_database(
            self.databases[NotionDatabaseEnum.TRANSACTIONS.value]['id'],
            start_cursor=cursor,
            page_size=page_size,
            filter=filter,
            filter_properties=properties,
            sorts=[
                {
                    "property": "Criado em",
                    "direction": "descending"
                }
            ]
        )
        return self.__process_database_registers(data)
    
    def get_full_categories(self) -> dict:
        '''It's lazy because load a lot of data'''
        data = self.notion_repository.get_database(self.databases[NotionDatabaseEnum.CATEGORIES.value]['id'])
        return self.__process_database_registers(data)
    
    def get_months_by_year(self, year:int, property_ids: list[str] = []) -> dict:
        try:
            title_property_id = self.__get_title_property_from_schema(self.databases[NotionDatabaseEnum.MONTHS.value]['properties'])
            property_ids_parsed = [urllib.parse.unquote(id) for id in property_ids]
            data = self.notion_repository.get_database(
                self.databases[NotionDatabaseEnum.MONTHS.value]['id'],
                filter_properties=[title_property_id, *property_ids_parsed],
                filter={
                    'and':[{
                        'property': 'MesData',
                            'date': {'on_or_after': f"{year}"},
                        }]}
                )
            return self.__process_database_registers(data)
        except Exception as e:
            print(e)

    def get_simple_data(self, database:NotionDatabaseEnum, cursor: str = None):
        title_property_id = self.__get_title_property_from_schema(self.databases[database.value]['properties'])
        data = self.notion_repository.get_database(
            self.databases[database.value]['id'], 
            filter_properties=[title_property_id],
            start_cursor=cursor
        )
        return self.__process_database_registers(data)

    def get_properties(self, database: str) -> dict:
        full_properties = self.databases[database]['properties']
        properties = {}
        for key, value in full_properties.items():
            properties[key] = {
                "id":value["id"],
                "name":value["name"],
                "type":value["type"],
                "description":value.get("description", ""),
            }   
        return properties
    
    def get_current_month(self) -> dict:
        data = self.notion_repository.get_database(
            self.databases[NotionDatabaseEnum.MONTHS.value]['id'],
            filter={
                'and': [{
                'property': 'isMesAtual',
                'formula': {
                    'checkbox': {
                        'equals': True
                }}}]
            }    
        )
        return self.__process_database_registers(data)
    
    #TODO Simplficar esse metodo
    def create_out_transaction(self, name, month, amount,date,card,category,type):
        page = {
            "parent": {
                "type": "database_id",
                "database_id": self.databases[NotionDatabaseEnum.TRANSACTIONS.value]['id']
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": name
                            }
                        }
                    ]
                },
                "Categoria": {
                    "relation": [
                        {"id": category}
                    ]
                },
                "Mês": {
                    "relation": [
                        {"id": month}
                    ]
                },
                "Saida de": {
                    "relation": [
                        {"id": card}
                    ]
                },
                "Tipo Saida": {
                    "relation": [
                        {"id": type}
                    ]
                },
                "Valor": {
                    "number": amount
                },
                "Criado em": {
                    "date":{
                        "start": date
                    }
                },
                "Tipo Transação":{
                    "select":{
                        "name":"Saida",
                    }
                },
            },
        }

        self.notion_repository.create_page(page)

    def get_planning_by_month(self, month_id) -> dict:
        database_id = self.databases[NotionDatabaseEnum.PLANNING.value]['id']
        data = self.notion_repository.get_database(
            database_id,
            filter={
                'and': [{
                'property': 'Mes',
                'relation': {'contains':month_id}}]
            }    
        )
        return self.__process_database_registers(data)


    def __process_database_registers(self, data) -> dict:
        full_data = {
            'has_more': data['has_more'],
            'next_cursor': data['next_cursor']
        }
        registers = []
        self.cache = {}
        for item in data['results']:
            row = {}
            row['id'] = item['id']
            for key, value in item['properties'].items():
                property = BasicProperty(key, value)
                row[property.name] = property.value
                if property.property_type == 'relation' :
                    row[property.name] = [self.__get_page_name(page_id['id']) for page_id in property.value]
            registers.append(row)
        self.cache = {}
        full_data['data'] = registers
        return full_data
    
    def __get_page_name(self, page_id: str) -> str:
        if page_id in self.cache:
            return self.cache[page_id]
        
        name = "not_found"
        self.cache[page_id] = name
        data = self.notion_repository.get_page(page_id)
        for key, value in data['properties'].items():
            if value['type'] == 'title':
                name = value['title'][0]['plain_text']
                self.cache[page_id] = name
        return name

    def __get_title_property_from_schema(self, schema:dict) -> str:
        for key, value in schema.items():
            if value['type'] == 'title':
                return value['id']
        return None
