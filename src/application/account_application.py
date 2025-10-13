from uuid import UUID
from typing import TYPE_CHECKING, List

from domain import AccountDomain, TransactionDomain
from dto.aggregates.accout_with_balance_aggregate import AccountWithBalanceAggregate
from repository import AccountModel
from datetime import datetime

if TYPE_CHECKING:
    from controllers.request_models.account import AccountRequest


class AccountApplication:
    def __init__(self, domain: AccountDomain, transaction_domain: TransactionDomain):
        self.__domain = domain
        self.__transaction_domain = transaction_domain

    async def create(self, data: "AccountRequest") -> AccountModel:
        data_dict = data.model_dump()
        account = AccountModel(**data_dict)
        return await self.__domain.create(account)

    async def update(self, account_id: UUID, data: "AccountRequest") -> AccountModel:
        data_dict = data.model_dump()
        account = AccountModel(**data_dict)
        account.id = account_id

        return await self.__domain.update(account)

    async def delete(self, account_id: UUID, user_id: UUID) -> None:
        await self.__domain.delete(account_id, user_id)

    async def get_by_ids(self, account_ids: list[UUID]) -> list[AccountModel]:
        return await self.__domain.get_by_ids(account_ids)

    async def get_by_user_id(self, user_id: UUID) -> list[AccountModel]:
        return await self.__domain.get_by_user_id(user_id, withDeleted=True)
    
    async def get_accounts_with_balance(self, user_id: UUID) -> List[AccountWithBalanceAggregate]:
        accounts = await self.__domain.get_by_user_id(user_id)

        accounts_with_balance: List[AccountWithBalanceAggregate] = []
        for account in accounts:
            account_with_balance = AccountWithBalanceAggregate.model_validate(account)
            # TODO: Muito ineficiente - Preciso modificar a estrutura de transações
            # para agregar esses dados com uma busca direta no banco
            total_income = await self.__transaction_domain.sum_transactions_from_destination_account(account.id, user_id)
            total_outcome = await self.__transaction_domain.sum_transactions_from_source_account(account.id, user_id)

            account_balance = (total_income - total_outcome) + float(account.opening_balance_cents)
            account_with_balance.balance_cents = account_balance
            account_with_balance.balance_date = datetime.now()

            accounts_with_balance.append(account_with_balance)

        return accounts_with_balance
        



