from .notion_external import NotionExternal

class NotionAuthorizationData:
    def __init__(self,notion_external: NotionExternal):
        self.__notion_external = notion_external

    async def get_all_databases(self):
        return self.__notion_external.get_all_databases()