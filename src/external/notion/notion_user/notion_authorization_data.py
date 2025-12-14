from ..notion_base_access.notion_external import NotionExternal

class NotionAuthorizationData:
    def __init__(self,notion_external: NotionExternal):
        self.__notion_external = notion_external

    async def get_all_data_sources(self):
        return await self.__notion_external.get_all_data_sources()
