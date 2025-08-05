import uuid
from repository import PluggyItemModel, PluggyAccountModel, PluggyItemRepository, PluggyTransactionModel

class PluggyItemDomain:
    def __init__(self, repository: PluggyItemRepository):
        self.__repository = repository

    async def create_if_not_exist(self, pluggy_item: PluggyItemModel) -> PluggyItemModel | None:
        exist_item = await self.__repository.get_pluggy_item_by_item_id(pluggy_item.item_id)
        if not exist_item:
            pluggy_item.id = uuid.uuid4()
            await self.__repository.create_pluggy_item(pluggy_item)
            return pluggy_item
        else:
            return None
        
    async def create_accounts(self, accounts: list[PluggyAccountModel]):
        await self.__repository.create_accounts(accounts)

    async def create_transactions(self, transactions: list[PluggyTransactionModel]):
        await self.__repository.create_transactions(transactions)
