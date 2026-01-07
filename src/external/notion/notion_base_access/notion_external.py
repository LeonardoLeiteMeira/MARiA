from notion_client import AsyncClient
from ..models import NotionProperties, NotionBaseDatasource

class NotionExternal:
    def __init__(self, notion_client: AsyncClient):
        self.notion_client = notion_client
        self.cache = {}

    async def get_datasource(
        self,
        datasource_id: str,
        filter_properties: list = None,
        filter: dict = None,
        sorts: list = [],
        start_cursor: str = None,
        page_size: int = 30,
    ) -> dict:
        query = {
            "data_source_id": datasource_id,
            "sorts": sorts,
            "start_cursor": start_cursor,
            "page_size": page_size
        }

        if filter_properties:
            query["filter_properties"] = filter_properties
        if filter:
            query["filter"] = filter

        data = await self.notion_client.data_sources.query(**query)
        return data

    async def get_page(self, page_id: str) -> dict:
        data = await self.notion_client.pages.retrieve(
            **{
                "page_id": page_id
            }
        )
        return data
    
    async def retrieve_datasource(self, datasource_id: str) -> dict:
        return await self.notion_client.data_sources.retrieve(datasource_id)
    
    async def create_page(self, page: dict) -> dict:
        page["children"] = [{
                "object": "block",
                "heading_1": {
                    "rich_text": [
                        {
                            "text": {
                                "content": "Pagina criada por MARiA"
                            }
                        }]}},]
        response = await self.notion_client.pages.create(**page)
        return response

    async def process_datasource_registers(self, data) -> dict:
        full_data = {
            'has_more': data['has_more'],
            'next_cursor': data['next_cursor']
        }
        registers = []
        for item in data['results']:
            page_processed = await self.process_page_register(item)
            registers.append(page_processed)
        full_data['data'] = registers
        return full_data
    
    async def process_page_register(self, page):
        row = {}
        row['id'] = page['id']
        for key, value in page['properties'].items():
            property = NotionProperties(key, value)
            row[property.key] = property.value
            if property.property_type == 'relation':
                row[property.key] = [await self.__get_page_name(page_id['id']) for page_id in property.value]
        return row
    
    async def __get_page_name(self, page_id: str) -> str:
        if page_id in self.cache:
            return self.cache[page_id]
        
        name = "not_found"
        self.cache[page_id] = name
        data = await self.get_page(page_id)
        for key, value in data['properties'].items():
            if value['type'] == 'title':
                name = value['title'][0]['plain_text']
                self.cache[page_id] = name
        return name
    
    async def delete_page(self, page_id: str) -> None:
        await self.notion_client.pages.update(page_id=page_id, archived=True)

    async def get_all_data_sources(self) -> list[NotionBaseDatasource]:
        payload = {
            "filter": {"property": "object", "value": "data_source"},
            "page_size": 20
        }
        search_result = await self.notion_client.search(**payload)
        datasources = []
        for result in search_result['results']:
            datasources.append(
                NotionBaseDatasource(
                    name=result['title'][0]['text']['content'],
                    id=result['id']
                )
            )
        return datasources
