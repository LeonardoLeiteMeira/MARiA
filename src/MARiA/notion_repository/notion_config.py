import os
from notion_client import Client
from dotenv import load_dotenv
from MARiA.notion_repository.notion_repository import NotionRepository
from MARiA.notion_repository.notion_access import NotionAccess
from MARiA.notion_types import NotionDatabaseEnum
from datetime import datetime

load_dotenv()

api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

repo = NotionRepository(notion)
notion_access = NotionAccess(repo)

if __name__ == '__main__':
    data = notion_access.get_properties('months')
    print(data)
