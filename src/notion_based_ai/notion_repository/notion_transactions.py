from notion_based_ai.notion_types import Database
from .notion_repository import NotionRepository
from .basic_property import BasicProperty

class NotionTransaction:
    def __init__(self, notion_repository: NotionRepository):
        self.notion_repository = notion_repository
        self.databases = {
            Database.TRANSACTIONS.value: {
                "id": "97c5aad2c46d46a49c3b78e83473ae52"
            },
            Database.CATEGORIES.value : {
                "id": "38236d860412473fa9f8d3a0f1e4b0e1"
            },
            Database.MONTHS.value : {
                "id": "d91b81e32555418a8bb62a76d7c69ac7"
            },
            Database.CARDS.value: {
                "id" : "d1f6611fa1c046eb8cdf87ba3c757f6b"
            },
            Database.TYPES.value: {
                'id': '6852342492704ecf8205c6ac953cf3a2'
            }
        }
        self.cache = {}
        self.__load_database_schema()

    def __load_database_schema(self) -> dict:
        for key, value in self.databases.items():
            data = self.notion_repository.retrieve_databse(value['id'])
            value['properties'] = data['properties']

    def get_transactions(self) -> dict:
        data = self.notion_repository.get_database(self.databases[Database.TRANSACTIONS.value]['id'])
        return self.__process_database_registers(data)
    
    def get_full_categories(self) -> dict:
        data = self.notion_repository.get_database(self.databases[Database.CATEGORIES.value]['id'])
        return self.__process_database_registers(data)
    
    def get_months_by_year(self, year:int, property_ids: list[str] = []) -> dict:
        title_property_id = self.__get_title_property_from_schema(self.databases[Database.MONTHS.value]['properties'])
        data = self.notion_repository.get_database(
            self.databases[Database.MONTHS.value]['id'],
            filter_properties=[title_property_id, *property_ids],
            filter={
                'and':[{
                    'property': 'MesData',
                        'date': {'on_or_after': f"{year}"},
                    }]}        
            )
        return self.__process_database_registers(data)

    def get_simple_data(self, database:Database):
        title_property_id = self.__get_title_property_from_schema(self.databases[database.value]['properties'])
        data = self.notion_repository.get_database(self.databases[database.value]['id'], filter_properties=[title_property_id])
        return self.__process_database_registers(data)

    def get_properties(self, database: str) -> dict:
        return self.databases[database]['properties']
    
    def get_current_month(self) -> dict:
        data = self.notion_repository.get_database(
            self.databases[Database.MONTHS.value]['id'],
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
    
    def create_out_transaction(self, data: dict):
        for key, value in data.items():
            pass
        properties = self.databases[Database.TRANSACTIONS.value]['properties']
        for key, value in properties.items():
            print(key, value)

    def __process_database_registers(self, data) -> dict:
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
        return registers
    
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
