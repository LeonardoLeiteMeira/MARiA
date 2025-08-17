from uuid import UUID
from typing import TYPE_CHECKING

from domain import AccountDomain
from repository import AccountModel

if TYPE_CHECKING:
    from controllers.request_models.account import AccountRequest


class AccountApplication:
    """Application layer for account operations."""

    def __init__(self, domain: AccountDomain):
        self._domain = domain

    async def create(self, data: "AccountRequest") -> AccountModel:
        # Convert API payload into domain model before persisting
        account = AccountModel(
            user_id=data.user_id,
            type=data.type,
            opening_balance_cents=data.opening_balance_cents,
            icon=data.icon,
            currency=data.currency,
        )
        return await self._domain.create(account)

    async def update(self, account_id: UUID, data: "AccountRequest") -> AccountModel:
        account = AccountModel(
            id=account_id,
            user_id=data.user_id,
            type=data.type,
            opening_balance_cents=data.opening_balance_cents,
            icon=data.icon,
            currency=data.currency,
        )
        return await self._domain.update(account)

    async def delete(self, account_id: UUID, user_id: UUID) -> None:
        # ensure repository filters by both id and owner
        await self._domain.delete(account_id, user_id)

    async def get_by_ids(self, account_ids: list[UUID]) -> list[AccountModel]:
        return await self._domain.get_by_ids(account_ids)

    async def get_by_user_id(self, user_id: UUID) -> list[AccountModel]:
        return await self._domain.get_by_user_id(user_id)
