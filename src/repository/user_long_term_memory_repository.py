import uuid
from typing import cast

from sqlalchemy import select, update

from .base_repository import BaseRepository
from .db_models.user_long_term_memory_model import UserLongTermMemoryModel


class UserLongTermMemoryRepository(BaseRepository):
    async def get_by_user_id(
        self, user_id: str | uuid.UUID
    ) -> UserLongTermMemoryModel | None:
        normalized_user_id = self.__normalize_user_id(user_id)
        stmt = select(UserLongTermMemoryModel).where(
            UserLongTermMemoryModel.user_id == normalized_user_id
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def upsert_user_memory(
        self,
        user_id: str | uuid.UUID,
        memory_json: dict[str, str],
    ) -> UserLongTermMemoryModel:
        normalized_user_id = self.__normalize_user_id(user_id)
        existing = await self.get_by_user_id(normalized_user_id)

        async with self.session() as session:
            if existing is None:
                model = UserLongTermMemoryModel(
                    user_id=normalized_user_id,
                    memory_json=memory_json,
                )
                session.add(model)
                await session.commit()
                await session.refresh(model)
                return model

            stmt = (
                update(UserLongTermMemoryModel)
                .where(UserLongTermMemoryModel.user_id == normalized_user_id)
                .values({"memory_json": memory_json})
                .returning(UserLongTermMemoryModel)
            )
            cursor = await session.execute(stmt)
            await session.commit()
            return cast(UserLongTermMemoryModel, cursor.scalars().first())

    def __normalize_user_id(self, user_id: str | uuid.UUID) -> uuid.UUID:
        if isinstance(user_id, uuid.UUID):
            return user_id
        return uuid.UUID(str(user_id))
