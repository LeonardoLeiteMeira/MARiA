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

    # def create_page(self, database_id: str, properties: Dict[str, Any]) -> NotionPage:
    #     response = self.notion_client.create_page(database_id, properties)
    #     return NotionPage(response)

    # def update_page(self, page_id: str, properties: Dict[str, Any]) -> NotionPage:
    #     response = self.notion_client.update_page(page_id, properties)
    #     return NotionPage(response)

    # def delete_page(self, page_id: str) -> None:
    #     self.notion_client.delete_page(page_id)