from repository import NotionAuthorizationRepository, NotionAuthorizationModel


class NotionAuthorizationDomain:
    def __init__(self, repo: NotionAuthorizationRepository):
        self._repo = repo

    async def save(self, record: NotionAuthorizationModel) -> None:
        await self._repo.create(record)
