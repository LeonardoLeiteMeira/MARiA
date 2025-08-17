from typing import Sequence
import uuid

from sqlalchemy import select, update, delete

from .base_repository import BaseRepository
from .db_models.account_model import AccountModel


class AccountRepository(BaseRepository):
    async def create(self, account: AccountModel):
        async with self.session() as session:
            session.add(account)
            await session.commit()

    async def update(self, account: AccountModel):
        if account.id is None:
            raise Exception("account id is not defined")
        stmt = (
            update(AccountModel)
            .where(AccountModel.id == account.id)
            .values(account)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, account: AccountModel):
        if account.id is None:
            raise Exception("account id is not defined")
        stmt = (
            delete(AccountModel)
            .where(AccountModel.id == account.id)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, account_id: uuid.UUID) -> AccountModel | None:
        stmt = (
            select(AccountModel)
            .where(AccountModel.id == account_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def get_by_ids(self, account_ids: Sequence[uuid.UUID]) -> list[AccountModel]:
        if not account_ids:
            return []
        stmt = select(AccountModel).where(AccountModel.id.in_(account_ids))
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[AccountModel]:
        stmt = select(AccountModel).where(AccountModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
