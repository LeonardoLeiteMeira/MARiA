from uuid import UUID
from typing import TYPE_CHECKING

from domain import TransactionDomain
from repository import TransactionModel
from dto import PaginatedDataListDto
from dto.models import TransactionDto

if TYPE_CHECKING:
    from controllers.request_models.transaction import TransactionRequest, TransactionFilter


class TransactionApplication:
    """Application layer for transaction operations."""

    def __init__(self, domain: TransactionDomain):
        self._domain = domain

    async def create(self, data: "TransactionRequest") -> TransactionModel:
        trx = TransactionModel(
            user_id=data.user_id,
            name=data.name,
            amount_cents=data.amount_cents,
            occurred_at=data.occurred_at,
            category_id=data.category_id,
            macro_category_id=data.macro_category_id,
            type=data.type,
            management_period_id=data.management_period_id,
            source_account_id=data.source_account_id,
            destination_account_id=data.destination_account_id,
            tags=data.tags,
            currency=data.currency,
        )
        return await self._domain.create(trx)

    async def update(self, transaction_id: UUID, data: "TransactionRequest") -> TransactionModel:
        trx = TransactionModel(
            id=transaction_id,
            user_id=data.user_id,
            name=data.name,
            amount_cents=data.amount_cents,
            occurred_at=data.occurred_at,
            category_id=data.category_id,
            macro_category_id=data.macro_category_id,
            type=data.type,
            management_period_id=data.management_period_id,
            source_account_id=data.source_account_id,
            destination_account_id=data.destination_account_id,
            tags=data.tags,
            currency=data.currency,
        )
        return await self._domain.update(trx)

    async def delete(self, transaction_id: UUID, user_id: UUID) -> None:
        await self._domain.delete(transaction_id, user_id)

    async def get_by_ids(self, transaction_ids: list[UUID]) -> list[TransactionModel]:
        return await self._domain.get_by_ids(transaction_ids)

    async def get_user_transactions_with_filter(self, filter: "TransactionFilter") -> PaginatedDataListDto[TransactionDto]:
        return await self._domain.get_user_transactions_with_filter(filter)
