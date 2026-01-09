from typing import Sequence
import uuid

from sqlalchemy import select, update, delete, inspect

from .base_repository import BaseRepository
from .db_models.account_model import AccountModel


class AccountRepository(BaseRepository):
    async def create(self, account: AccountModel) -> None:
        async with self.session() as session:
            session.add(account)
            await session.commit()

    async def update(self, account: AccountModel) -> None:
        if account.id is None:
            raise Exception("account id is not defined")

        # Convert model instance into a dict excluding immutable identifiers
        mapper = inspect(AccountModel)
        cols = [c.key for c in mapper.attrs]
        data = {
            c: getattr(account, c)
            for c in cols
            if c not in ("id", "user_id") and getattr(account, c) is not None
        }

        stmt = (
            update(AccountModel)
            .where(
                AccountModel.id == account.id,
                AccountModel.user_id == account.user_id,
            )
            .values(**data)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, account: AccountModel) -> None:
        if account.id is None:
            raise Exception("account id is not defined")
        stmt = delete(AccountModel).where(
            AccountModel.id == account.id,
            AccountModel.user_id == account.user_id,
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, account_id: uuid.UUID) -> AccountModel | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id)
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

    async def get_by_user_id(
        self, user_id: uuid.UUID, withDeleted: bool = False
    ) -> list[AccountModel]:
        stmt = select(AccountModel)
        if withDeleted:
            stmt.where(AccountModel.user_id == user_id)
        else:
            stmt.where(
                AccountModel.user_id == user_id,
                AccountModel.deleted_at != None,
            )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
