from repository import NotionAuthorizationRepository, NotionAuthorizationModel


class NotionAuthorizationDomain:
    def __init__(self, notion_auth_repo: NotionAuthorizationRepository):
        self.__notion_auth_repo = notion_auth_repo

    async def save(self, record: NotionAuthorizationModel) -> None:
        await self.__notion_auth_repo.create(record)

    async def update(self, record: NotionAuthorizationModel) -> None:
        await self.__notion_auth_repo.update(record)

    async def get_by_bot_id(self, bot_id: str) -> NotionAuthorizationModel | None:
        return await self.__notion_auth_repo.get_by_bot_id(bot_id)
