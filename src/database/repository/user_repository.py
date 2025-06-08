from database.repository.base_repository import BaseRepository
from database.db_models.user_model import UserModel
from database.db_models.thread_model import ThreadModel
from sqlalchemy import text, Column, String, Integer, select, update, delete, desc
from sqlalchemy.orm import aliased, joinedload
from datetime import datetime, timedelta, timezone
import uuid


class UserRepository(BaseRepository):
    async def create_user(self, user: UserModel):
        async with self.session() as session:
            session.add(user)
            await session.commit()

    async def update_user(self, user: UserModel):
        if user.id is None:
            raise "user id is not defined"
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(user)
            .execution_options(synchronize_session="fetch")
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_user_by_id(self, user_id:str) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
        user_tuple = cursor.first()
        if user_tuple:
            return user_tuple[0]
        return None

    async def get_user_by_phone_number(self, phone_number:str) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.phone_number == phone_number)
            .execution_options(synchronize_session="fetch")
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            user_tuple = cursor.first()
        if user_tuple:
            return user_tuple[0]
        return None
    

    async def get_user_last_thread_by_phone_number(self, phone_number: str) -> ThreadModel | None:
        now = datetime.now()
        valid_thread_period = now - timedelta(minutes=1)
        stmt = (
            select(ThreadModel)
            .join(UserModel, ThreadModel.user_id == UserModel.id)
            .where(
                ThreadModel.updated_at > valid_thread_period,
                UserModel.phone_number == phone_number
            )
            .order_by(desc(ThreadModel.updated_at))
            .limit(1)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            thread_tuple = cursor.scalars().all()
        print(thread_tuple)
        if thread_tuple:
            return thread_tuple
        return None
    

    async def create_user_new_thread(self, user_id: str):
        new_thread = ThreadModel(
            thread_id=uuid.uuid4(),
            user_id=user_id,
            status='open',
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(hours=-3),
            updated_at=datetime.now() - timedelta(hours=-3),
        )
    
        async with self.session() as session:
            session.add(new_thread)
            await session.commit()

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