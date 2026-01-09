from typing import Sequence
import uuid

from sqlalchemy import select, update, delete, inspect, func

from dto import PaginatedDataListDto
from dto.models import TransactionDto

from .base_repository import BaseRepository
from .db_models.transaction_model import TransactionModel
from .mixin import TransactionFilterToSqlAlchemyMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.request_models.transaction import TransactionFilter

class TransactionRepository(BaseRepository, TransactionFilterToSqlAlchemyMixin):
    async def create(self, transaction: TransactionModel) -> None:
        async with self.session() as session:
            session.add(transaction)
            await session.commit()

    async def update(self, transaction: TransactionModel) -> None:
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

    async def delete(self, transaction: TransactionModel) -> None:
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

    async def get_user_transactions_with_filter(self, filter: "TransactionFilter") -> PaginatedDataListDto[TransactionDto]:
        stmt = select(TransactionModel)
        stmt = self.apply_transaction_filters(stmt, filter, TransactionModel)
        async with self.session() as session:
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total_count = total_result.scalar_one()

            stmt = self.apply_pagination(stmt, filter)
            cursor = await session.execute(stmt)
            transaction_list = list(cursor.scalars().all())

        transaction_list_dto = [TransactionDto.model_validate(model) for model in transaction_list]

        paginated_list = PaginatedDataListDto(
            total_count=total_count,
            page_size=len(transaction_list),
            page=filter.page,
            list_data=transaction_list_dto
        )

        return paginated_list
    
    async def sum_transactions_amount_by_filter(self, filter: "TransactionFilter") -> float:
        stmt = select(func.coalesce(func.sum(TransactionModel.amount_cents), 0))
        stmt = self.apply_transaction_filters(stmt, filter, TransactionModel)
        stmt = stmt.order_by(None)
        async with self.session() as session:
            result = await session.execute(stmt)
            total = result.scalar()
        return float(total or 0)
