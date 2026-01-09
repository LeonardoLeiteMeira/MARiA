from .base_repository import BaseRepository
from .db_models.user_model import UserModel
from .db_models.thread_model import ThreadModel
from .db_models.notion_datasource_model import NotionDatasourceModel
from sqlalchemy import text, Column, String, Integer, select, update, delete, desc
from sqlalchemy.orm import joinedload, selectinload, with_loader_criteria
from datetime import datetime
from typing import Any, cast


class UserRepository(BaseRepository):
    async def create_user(self, user: UserModel) -> None:
        async with self.session() as session:
            session.add(user)
            await session.commit()

    async def update_user(self, user: UserModel) -> None:
        if user.id is None:
            raise ValueError("user id is not defined")
        stmt = update(UserModel).where(UserModel.id == user.id).values(cast(Any, user))
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_user_by_id(self, user_id: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            user_tuple: Any = cursor.scalars().first()
            return user_tuple[0] if user_tuple else None

    async def get_user_by_phone_number_with_notion_data(
        self, phone_number: str
    ) -> UserModel | None:
        stmt = (
            select(UserModel)
            .options(joinedload(UserModel.notion_authorization))
            .options(selectinload(UserModel.notion_datasources))
            .options(
                with_loader_criteria(
                    NotionDatasourceModel,
                    NotionDatasourceModel.tag.isnot(None),
                    include_aliases=True,
                )
            )
            .where(UserModel.phone_number == phone_number)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            user = cursor.scalars().first()
            return user if user else None

    async def get_user_valid_threads_by_user_id(
        self,
        user_id: str,
        last_valid_date: datetime,
    ) -> list[ThreadModel]:
        stmt = (
            select(ThreadModel)
            .where(
                ThreadModel.user_id == user_id,
                ThreadModel.updated_at >= last_valid_date,
            )
            .order_by(desc(ThreadModel.updated_at))
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def create_user_new_thread(self, new_thread: ThreadModel) -> ThreadModel:
        async with self.session() as session:
            session.add(new_thread)
            await session.commit()
        return new_thread

    async def update_thread_model_updated_at(self, thread_id: str) -> Any:
        new_updated_at = datetime.now()
        stmt = (
            update(ThreadModel)
            .where(ThreadModel.id == thread_id)
            .values({"updated_at": new_updated_at})
            .returning(ThreadModel)
        )
        async with self.session() as session:
            data = await session.execute(stmt)
            await session.commit()
            return data

    async def get_all_users(self) -> list[UserModel]:
        async with self.session() as session:
            stmt = select(UserModel)
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    # async def get_user_with_last_thread(self, phone_number: str):
    #     last_thread_subq = (
    #         select(ThreadModel)\
    #         .where(ThreadModel.user_id == UserModel.id)\
    #         .order_by(desc(ThreadModel.created_at))\
    #         .limit(1)\
    #         .correlate(UserModel)\
    #         .subquery()
    #     )

    #     LastThread = aliased(ThreadModel, last_thread_subq)

    #     stmt1 = (
    #         select(UserModel, LastThread)\
    #         .join(LastThread, LastThread.user_id == UserModel.id)\
    #         .where(UserModel.phone_number == phone_number)
    #     )

    #     stmt2 = (
    #         select(UserModel)
    #         .options(joinedload(UserModel.threads))
    #         .where(UserModel.phone_number == phone_number)
    #     )

    #     return await self._base_db.session.execute(stmt2)
