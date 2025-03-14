import os
from notion_client import Client
from dotenv import load_dotenv
from notion_based_ai.notion_repository.notion_repository import NotionRepository
from notion_based_ai.notion_repository.notion_access import NotionAccess
from notion_based_ai.notion_types import Database
from datetime import datetime

load_dotenv()

api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

repo = NotionRepository(notion)
notion_access = NotionAccess(repo)


#TODO proximo passo sera criar uma transacao no notion

if __name__ == '__main__':
    data = notion_access.get_planning_by_month('1ad14f69-1c83-80ea-aeb6-e5db9ed427a2')
    print(data)