from .base_repository import BaseRepository
from .db_models.notion_authorization_model import NotionAuthorizationModel


class NotionAuthorizationRepository(BaseRepository):
    async def create(self, auth: NotionAuthorizationModel):
        async with self.session() as session:
            session.add(auth)
            await session.commit()
