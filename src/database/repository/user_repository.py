from database.repository.base_repository import BaseRepository
from database.db_models.user_model import UserModel
from database.db_models.thread_model import ThreadModel
from sqlalchemy import text, Column, String, Integer, select, update, delete, desc
from sqlalchemy.orm import aliased, joinedload
from datetime import datetime, timedelta
import uuid


class UserRepository(BaseRepository):
    async def create_user(self, user: UserModel):
        await self._execute_in_transaction(self._create_user, user)

    async def _create_user(self, user: UserModel):
        self._base_db.session.add(user)

    async def update_user(self, user: UserModel):
        if user.id is None:
            raise "user id is not defined"
        await self._execute_in_transaction(self._update_user, user)

    async def _update_user(self, user: UserModel):
        stmt = (
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(user)
            .execution_options(synchronize_session="fetch")
        )
        await self._base_db.session.execute(stmt)

    async def get_user_by_id(self, user_id:str) -> UserModel | None:
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        cursor = await self._base_db.session.execute(stmt)
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
        session = self._base_db.session
        cursor = await session.execute(stmt)
        await session.close()
        user_tuple = cursor.first()
        if user_tuple:
            return user_tuple[0]
        return None
    

    async def get_user_last_thread_by_phone_number(self, phone_number: str) -> ThreadModel | None:
        now = datetime.now()
        valid_thread_period = now - timedelta(hours=3)
        stmt = (
            select(ThreadModel)
            .join(UserModel, ThreadModel.user_id == UserModel.id)
            .where(
                ThreadModel.updated_at > valid_thread_period,
                UserModel.phone_number == phone_number
            )
            .order_by(desc(ThreadModel.created_at))
            .limit(1)
        )
        session = self._base_db.session
        cursor = await session.execute(stmt)
        thread_tuple = cursor.first()
        await session.close()
        if thread_tuple:
            return thread_tuple[0]
        return None
    

    async def create_user_new_thread(self, user_id: str):
        new_thread = ThreadModel(
            thread_id=uuid.uuid4(),
            user_id=user_id,
            status='open',
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        # await self._execute_in_transaction(self._create_thread, new_thread)

        # session = self._base_db.session
        # trans = await session.begin()
        # trans.session.add(new_thread)
        # await trans.commit()
        # await session.close()
    
        session = self._base_db.session
        session.add(new_thread)
        await session.commit()
        await session.close()








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