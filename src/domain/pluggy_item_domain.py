import uuid
from repository import (
    PluggyItemModel,
    PluggyAccountModel,
    PluggyItemRepository,
    PluggyTransactionModel,
    PluggyCardBillModel,
    PluggyInvestmentModel,
    PluggyInvestmentTransactionModel,
    PluggyLoanModel,
)

class PluggyItemDomain:
    def __init__(self, repository: PluggyItemRepository) -> None:
        self.__repository = repository

    async def create_if_not_exist(self, pluggy_item: PluggyItemModel) -> PluggyItemModel | None:
        exist_item = await self.__repository.get_pluggy_item_by_item_id(pluggy_item.id)
        if not exist_item:
            await self.__repository.create_pluggy_item(pluggy_item)
            return pluggy_item
        else:
            return None
        
    async def create_accounts(self, accounts: list[PluggyAccountModel]) -> None:
        await self.__repository.create_accounts(accounts)

    async def create_transactions(self, transactions: list[PluggyTransactionModel]) -> None:
        await self.__repository.create_transactions(transactions)

    async def create_bills(self, bills: list[PluggyCardBillModel]) -> None:
        await self.__repository.create_bills(bills)

    async def create_investments(self, investments: list[PluggyInvestmentModel]) -> None:
        await self.__repository.create_investments(investments)

    async def create_investment_transactions(
        self,
        transactions: list[PluggyInvestmentTransactionModel],
    ) -> None:
        await self.__repository.create_investment_transactions(transactions)

    async def create_loans(self, loans: list[PluggyLoanModel]) -> None:
        await self.__repository.create_loans(loans)

    async def get_accounts(self, user_id: uuid.UUID) -> list[PluggyAccountModel]:
        return await self.__repository.get_accounts_by_user(user_id)

    async def get_transactions(self, user_id: uuid.UUID, account_id: uuid.UUID) -> list[PluggyTransactionModel]:
        return await self.__repository.get_transactions_by_account(user_id, account_id)

    async def get_bills(self, user_id: uuid.UUID, account_id: uuid.UUID) -> list[PluggyCardBillModel]:
        return await self.__repository.get_bills_by_account(user_id, account_id)

    async def get_investments(self, user_id: uuid.UUID) -> list[PluggyInvestmentModel]:
        return await self.__repository.get_investments_by_user(user_id)

    async def get_investment_transactions(self, user_id: uuid.UUID, investment_id: uuid.UUID) -> list[PluggyInvestmentTransactionModel]:
        return await self.__repository.get_investment_transactions(user_id, investment_id)

    async def get_loans(self, user_id: uuid.UUID) -> list[PluggyLoanModel]:
        return await self.__repository.get_loans_by_user(user_id)
