from database.repository.base_repository import BaseRepository
from database.db_models.user_model import UserModel
from sqlalchemy import text, Column, String, Integer, select, update, delete


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
        self._base_db.session.execute(stmt)

    async def get_user_by_id(self, user_id:str):
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        self._base_db.session.execute(stmt)

    async def get_user_by_phone_number(self, phone_number:str):
        stmt = (
            select(UserModel)
            .where(UserModel.phone_number == phone_number)
            .execution_options(synchronize_session="fetch")
        )
        self._base_db.session.execute(stmt)