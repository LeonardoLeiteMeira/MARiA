from .notion_repository import NotionRepository
from .basic_property import BasicProperty

class NotionTransaction:
    def __init__(self, notion_repository: NotionRepository):
        self.notion_repository = notion_repository
        self.databases = [
            {
                "name": "transactions",
                "id": "97c5aad2c46d46a49c3b78e83473ae52"
            },
            {
                "name": "categories",
                "id": "38236d860412473fa9f8d3a0f1e4b0e1"
            },
            {
                "name": "months",
                "id": "d91b81e32555418a8bb62a76d7c69ac7"
            }
        ]
        self.cache = {}
        self.load_database_schema()

    def load_database_schema(self) -> dict:
        for database in self.databases:
            data = self.notion_repository.retrieve_databse(database['id'])
            database['properties'] = data['properties']
        return data

    def get_transactions(self) -> dict:
        data = self.notion_repository.get_database(self.databases[0]['id'])
        return self.__process_database_registers(data)
    
    def get_full_categories(self) -> dict:
        data = self.notion_repository.get_database(self.databases[1]['id'])
        return self.__process_database_registers(data)
    
    def get_simple_categories(self) -> dict:
        title_property_id = ""
        for key, value in self.databases[1]['properties'].items():
            if value['type'] == 'title':
                title_property_id = value['id']
                break
        data = self.notion_repository.get_database(self.databases[1]['id'], filter_properties=[title_property_id])
        return self.__process_database_registers(data)
    
    def get_current_month(self) -> dict:
        data = self.notion_repository.get_database(
            self.databases[2]['id'],
            filter={
                'and': [
                    {
                        'property': 'isMesAtual',
                        'formula': {
                            'checkbox': {
                                'equals': True
                            }
                        }
                    }
                ]
            }    
        )
        return self.__process_database_registers(data)
    
    def get_months(self) -> dict:
        data = self.notion_repository.get_database(
            self.databases[2]['id'],
            filter={
                'and': [
                    {
                        'property': 'title',
                        'title': {
                            'contains': 'fev'
                        }
                    },
                    {
                        'property': 'title',
                        'title': {
                            'contains': '2025'
                        }
                    }
                ]
            }    
        )
        return self.__process_database_registers(data)

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