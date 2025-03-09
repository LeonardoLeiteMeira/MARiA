import os
from notion_client import Client
from dotenv import load_dotenv
from notion_based_ai.notion_repository.notion_repository import NotionRepository
from notion_based_ai.notion_repository.notion_transactions import NotionTransaction
from notion_based_ai.notion_types import Database
from datetime import datetime

load_dotenv()

api_key = os.getenv("NOTION_API_KEY")

notion = Client(auth=api_key)

repo = NotionRepository(notion)
notion_transactio_repository = NotionTransaction(repo)


#TODO proximo passo sera criar uma transacao no notion

if __name__ == '__main__':
    data = notion_transactio_repository.create_out_transaction(
        "teste",
        "1ad14f69-1c83-80ea-aeb6-e5db9ed427a2",
        987654,
        datetime.now().isoformat(),
        "7741c900-281e-44f1-b478-492743ef4d84",
        "601f4cb1-da6a-43fa-abad-fd77181ad3ec",
        "9a341091-f519-4770-ae50-1299b3ec0278"
    )
    # print(data)