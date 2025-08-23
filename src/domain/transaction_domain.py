from uuid import UUID

from repository import TransactionRepository, TransactionModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controllers.request_models.transaction import TransactionFilter


class TransactionDomain:
    """Domain layer for transaction operations."""

    def __init__(self, repo: TransactionRepository):
        self._repo = repo

    async def create(self, transaction: TransactionModel) -> TransactionModel:
        await self._repo.create(transaction)
        return transaction

    async def update(self, transaction: TransactionModel) -> TransactionModel:
        await self._repo.update(transaction)
        return transaction

    async def delete(self, transaction_id: UUID, user_id: UUID) -> None:
        transaction = TransactionModel(id=transaction_id, user_id=user_id)
        await self._repo.delete(transaction)

    async def get_by_ids(self, transaction_ids: list[UUID]) -> list[TransactionModel]:
        return await self._repo.get_by_ids(transaction_ids)

    async def get_user_transactions_with_filter(self, filter: "TransactionFilter") -> list[TransactionModel]:
        return await self._repo.get_user_transactions_with_filter(filter)
