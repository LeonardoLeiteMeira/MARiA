from notion_client import Client
from .basic_property import BasicProperty

class NotionRepository:
    def __init__(self, notion_client: Client):
        self.notion_client = notion_client

    def get_database(
        self,
        database_id: str,
        filter_properties: dict = None,
        filter: dict = None,
        sorts: list = [],
        start_cursor: dict = None,
        page_size: int = 10,
    ) -> dict:
        data = self.notion_client.databases.query(
            **{
                "database_id": database_id,
                # 'filter_properties': filter_properties,
                # "filter": filter,
                "sorts": sorts,
                "start_cursor": start_cursor,
                "page_size": page_size
            }
        )
        # registers = []
        # for item in data['results']:
        #     row = {}
        #     for key, value in item['properties'].items():
        #         property = BasicProperty(key, value)
        #         row[property.name] = property.value
        #     registers.append(row)
        # return registers

        return data

    def get_page(self, page_id: str) -> dict:
        data = self.notion_client.pages.retrieve( 
            **{
                "page_id": page_id
            }
        )
        return data

    # def get_pages(self, database_id: str) -> List[NotionPage]:
    #     response = self.notion_client.get_pages(database_id)
    #     return [NotionPage(page) for page in response]

    # def create_page(self, database_id: str, properties: Dict[str, Any]) -> NotionPage:
    #     response = self.notion_client.create_page(database_id, properties)
    #     return NotionPage(response)

    # def update_page(self, page_id: str, properties: Dict[str, Any]) -> NotionPage:
    #     response = self.notion_client.update_page(page_id, properties)
    #     return NotionPage(response)

    # def delete_page(self, page_id: str) -> None:
    #     self.notion_client.delete_page(page_id)