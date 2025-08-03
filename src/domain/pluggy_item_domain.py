import uuid
from repository import PluggyItemModel, PluggyItemRepository

class PluggyItemDomain:
    def __init__(self, repository: PluggyItemRepository):
        self.repository = repository

    async def create_if_not_exist(self, pluggy_item: PluggyItemModel) -> PluggyItemModel | None:
        exist_item = await self.repository.get_pluggy_item_by_item_id(pluggy_item.item_id)
        if not exist_item:
            pluggy_item.id = uuid.uuid4()
            await self.repository.create_pluggy_item(pluggy_item)
            return pluggy_item
        else:
            return None