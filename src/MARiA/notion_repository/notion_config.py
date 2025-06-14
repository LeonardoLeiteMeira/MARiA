from notion_client import Client
from config import get_settings
from MARiA.notion_repository.notion_repository import NotionRepository
from MARiA.notion_repository.notion_access import NotionAccess
from MARiA.notion_types import NotionDatabaseEnum
from MARiA.notion_repository.notion_user_data import NotionUserData
from datetime import datetime

settings = get_settings()

api_key = settings.notion_api_key

notion = Client(auth=api_key)

repo = NotionRepository(notion)
notion_access = NotionAccess(repo)

notion_user_data = NotionUserData(notion_access)

if __name__ == '__main__':
    id = "1eb14f691c8380e9ac19d38d787fd3b2"
    data = notion_access.get_page_by_id(id, ['Planejamentos', 'This (Não alterar)', 'Transações'])
    print(data)
