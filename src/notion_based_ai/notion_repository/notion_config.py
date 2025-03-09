import os
from notion_client import Client
from dotenv import load_dotenv
from notion_based_ai.notion_repository.notion_repository import NotionRepository
from notion_based_ai.notion_repository.notion_transactions import NotionTransaction
from notion_based_ai.notion_types import Database
load_dotenv()

api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

repo = NotionRepository(notion)
notion_transactio_repository = NotionTransaction(repo)


#TODO proximo passo sera criar uma transacao no notion
if __name__ == '__main__':
    data = notion_transactio_repository.get_months_by_year(2025, ['OzoZ'])
    print(data)