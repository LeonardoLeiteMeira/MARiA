import os
from notion_client import Client
from dotenv import load_dotenv

from notion_based_ai.notion_repository.basic_property import BasicProperty
from notion_based_ai.notion_repository.notion_repository import NotionRepository
from notion_based_ai.notion_repository.notion_transactions import NotionTransaction
load_dotenv()

api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

repo = NotionRepository(notion)
notion_transactio_repository = NotionTransaction(repo)

#TODO proximo passo sera criar uma transacao no notion

data = notion_transactio_repository.get_current_month()
print(data)