from notion_client import Client
from external.models import NotionProperties, NotionBaseDatabase

class NotionExternal:
    def __init__(self, notion_client: Client):
        self.notion_client = notion_client
        self.cache = {}

    def get_database(
        self,
        database_id: str,
        filter_properties: list = None,
        filter: dict = None,
        sorts: list = [],
        start_cursor: str = None,
        page_size: int = 30,
    ) -> dict:
        query = {
            "database_id": database_id,
            "sorts": sorts,
            "start_cursor": start_cursor,
            "page_size": page_size
        }

        if filter_properties:
            query["filter_properties"] = filter_properties
        if filter:
            query["filter"] = filter

        data = self.notion_client.databases.query(**query)
        return data

    def get_page(self, page_id: str) -> dict:
        data = self.notion_client.pages.retrieve( 
            **{
                "page_id": page_id
            }
        )
        return data
    
    def retrieve_databse(self, databse_id: str) -> dict:
        return self.notion_client.databases.retrieve(databse_id)
    
    def create_page(self, page: dict):
        page["children"] = [{
                "object": "block",
                "heading_1": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "Pagina criada por MARiA"
                            }
                        }]}},]
        response = self.notion_client.pages.create(**page)
        print(response)

    def process_database_registers(self, data) -> dict:
        full_data = {
            'has_more': data['has_more'],
            'next_cursor': data['next_cursor']
        }
        registers = []
        for item in data['results']:
            page_processed = self.process_page_register(item)
            registers.append(page_processed)
        full_data['data'] = registers
        return full_data
    
    def process_page_register(self, page):
        row = {}
        row['id'] = page['id']
        for key, value in page['properties'].items():
            property = NotionProperties(key, value)
            row[property.name] = property.value
            if property.property_type == 'relation' :
                row[property.name] = [self.__get_page_name(page_id['id']) for page_id in property.value]
        return row
    
    def __get_page_name(self, page_id: str) -> str:
        if page_id in self.cache:
            return self.cache[page_id]
        
        name = "not_found"
        self.cache[page_id] = name
        data = self.get_page(page_id)
        for key, value in data['properties'].items():
            if value['type'] == 'title':
                name = value['title'][0]['plain_text']
                self.cache[page_id] = name
        return name
    
    def delete_page(self, page_id: str) -> None:
        self.notion_client.pages.update(page_id=page_id, archived=True)

    def get_all_databases(self) -> list[NotionBaseDatabase]:
        payload = {
            "filter": {"property": "object", "value": "database"},
            "page_size": 20
        }
        search_result = self.notion_client.search(**payload)
        databases = []
        for result in search_result['results']:
            databases.append(
                NotionBaseDatabase(
                    name=result['title'][0]['text']['content'],
                    id=result['id']
                )
            )
        return databases

    # def create_page(self, database_id: str, properties: Dict[str, Any]) -> NotionPage:
    #     response = self.notion_client.create_page(database_id, properties)
    #     return NotionPage(response)

    # def update_page(self, page_id: str, properties: Dict[str, Any]) -> NotionPage:
    #     response = self.notion_client.update_page(page_id, properties)
    #     return NotionPage(response)
