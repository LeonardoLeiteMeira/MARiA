from database.repository.base_repository import BaseRepository
from database.db_models.user_model import UserModel
from database.db_models.thread_model import ThreadModel
from sqlalchemy import text, Column, String, Integer, select, update, delete, desc
from sqlalchemy.orm import aliased, joinedload
from datetime import datetime, timedelta


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

    async def get_user_by_id(self, user_id:str):
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        return await self._base_db.session.execute(stmt)

    async def get_user_by_phone_number(self, phone_number:str):
        stmt = (
            select(UserModel)
            .where(UserModel.phone_number == phone_number)
            .execution_options(synchronize_session="fetch")
        )
        return await self._base_db.session.execute(stmt)
    

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
        cursor = await self._base_db.session.execute(stmt)
        tuple = cursor.first()
        return tuple[0]
    

    async def create_new_thread_by_user_phone_number(self, phone_number: str):
        pass
    








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