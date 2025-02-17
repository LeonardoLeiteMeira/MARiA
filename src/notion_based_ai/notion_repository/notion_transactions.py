from .notion_repository import NotionRepository
from .basic_property import BasicProperty

class NotionTransaction:
    def __init__(self, notion_repository: NotionRepository):
        self.notion_repository = notion_repository
        self.database_id = "97c5aad2c46d46a49c3b78e83473ae52"
        self.cache = {}

    def get_transactions(self):
        data = self.notion_repository.get_database(self.database_id)
        registers = []
        self.cache = {}
        for item in data['results']:
            row = {}
            for key, value in item['properties'].items():
                property = BasicProperty(key, value)
                row[property.name] = property.value
                if(property.property_type == 'relation'):
                    row[property.name] = [self.get_page_name(page_id['id']) for page_id in property.value]
            registers.append(row)
        self.cache = {}
        return registers
    
    def get_page_name(self, page_id: str):
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