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

# print(notion_transactio_repository.get_transactions())

# data = notion.databases.query(
#     **{
#         "database_id": "97c5aad2c46d46a49c3b78e83473ae52"
#     }
# )

# transactions = []
# for item in data['results']:
#     transaction = []
#     for key, value in item['properties'].items():
#         property = BasicProperty(key, value)
#         transaction.append(property)
#     transactions.append(transaction)

# print(transactions)


# # Mes selecionado em uma transação
# # 19314f69-1c83-80e0-99e1-c2cd2867fd0e
# data = notion.pages.retrieve(
#     **{
#         "page_id": "19314f69-1c83-80e0-99e1-c2cd2867fd0e"
#     }
# )

# print(data)