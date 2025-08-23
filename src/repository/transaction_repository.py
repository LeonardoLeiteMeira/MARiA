from typing import Sequence
import uuid

from sqlalchemy import select, update, delete, inspect

from .base_repository import BaseRepository
from .db_models.transaction_model import TransactionModel
from .mixin import TransactionFilterToSqlAlchemyMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.request_models.transaction import TransactionFilter

class TransactionRepository(BaseRepository, TransactionFilterToSqlAlchemyMixin):
    async def create(self, transaction: TransactionModel):
        async with self.session() as session:
            session.add(transaction)
            await session.commit()

    async def update(self, transaction: TransactionModel):
        if transaction.id is None:
            raise Exception("transaction id is not defined")

        mapper = inspect(TransactionModel)
        cols = [c.key for c in mapper.attrs]
        data = {
            c: getattr(transaction, c)
            for c in cols
            if c not in ("id", "user_id") and getattr(transaction, c) is not None
        }

        stmt = (
            update(TransactionModel)
            .where(
                TransactionModel.id == transaction.id,
                TransactionModel.user_id == transaction.user_id,
            )
            .values(**data)
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def delete(self, transaction: TransactionModel):
        if transaction.id is None:
            raise Exception("transaction id is not defined")
        stmt = (
            delete(TransactionModel)
            .where(
                TransactionModel.id == transaction.id,
                TransactionModel.user_id == transaction.user_id,
            )
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_id(self, transaction_id: uuid.UUID) -> TransactionModel | None:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.id == transaction_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()

    async def get_by_ids(self, transaction_ids: Sequence[uuid.UUID]) -> list[TransactionModel]:
        if not transaction_ids:
            return []
        stmt = select(TransactionModel).where(TransactionModel.id.in_(transaction_ids))
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_user_transactions_with_filter(self, filter: "TransactionFilter") -> list[TransactionModel]:
        stmt = select(TransactionModel)
        stmt = self.apply_transaction_filters(stmt, filter, TransactionModel)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
