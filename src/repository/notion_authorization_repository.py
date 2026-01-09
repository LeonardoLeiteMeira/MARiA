from datetime import datetime
from sqlalchemy import select, update

from .base_repository import BaseRepository
from .db_models.notion_authorization_model import NotionAuthorizationModel


class NotionAuthorizationRepository(BaseRepository):
    async def create(self, auth: NotionAuthorizationModel) -> None:
        async with self.session() as session:
            session.add(auth)
            await session.commit()

    async def update(self, auth: NotionAuthorizationModel) -> None:
        stmt = (
            update(NotionAuthorizationModel)
            .where(NotionAuthorizationModel.id == auth.id)
            .values(
                user_id=auth.user_id,
                bot_id=auth.bot_id,
                _access_token=auth._access_token,
                workspace_id=auth.workspace_id,
                workspace_name=auth.workspace_name,
                workspace_icon=auth.workspace_icon,
                owner_type=auth.owner_type,
                owner_id=auth.owner_id,
                updated_at=datetime.now(),
            )
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_bot_id(self, bot_id: str) -> NotionAuthorizationModel | None:
        stmt = select(NotionAuthorizationModel).where(
            NotionAuthorizationModel.bot_id == bot_id
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()
