from uuid import UUID

from repository import AccountRepository, AccountModel, AccountType


class AccountDomain:
    """Domain layer for account operations."""

    def __init__(self, repo: AccountRepository):
        self._repo = repo

    async def create(self, account: AccountModel) -> AccountModel:
        await self._repo.create(account)
        return account

    async def update(self, account: AccountModel) -> AccountModel:
        await self._repo.update(account)
        return account

    async def delete(self, account_id: UUID) -> None:
        account = AccountModel(id=account_id)
        await self._repo.delete(account)

    async def get_by_ids(self, account_ids: list[UUID]) -> list[AccountModel]:
        return await self._repo.get_by_ids(account_ids)

    async def get_by_user_id(self, user_id: UUID) -> list[AccountModel]:
        return await self._repo.get_by_user_id(user_id)
