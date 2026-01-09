from .base_repository import BaseRepository
from .db_models.pluggy_item_model import PluggyItemModel
from .db_models.pluggy_account_model import PluggyAccountModel
from .db_models.pluggy_transactions_model import PluggyTransactionModel
from .db_models.pluggy_card_bill_model import PluggyCardBillModel
from .db_models.pluggy_investment_model import PluggyInvestmentModel
from .db_models.pluggy_investment_transaction_model import PluggyInvestmentTransactionModel
from .db_models.pluggy_loan_model import PluggyLoanModel

from sqlalchemy import text, Column, String, Integer, select, update, delete, desc

import uuid

class PluggyItemRepository(BaseRepository):
    async def get_pluggy_item_by_item_id(self, item_id: uuid.UUID) -> PluggyItemModel | None:
        stmt = (
            select(PluggyItemModel)
            .where(PluggyItemModel.id == item_id)
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()
        
    async def create_pluggy_item(self, new_pluggy_item: PluggyItemModel) -> None:
        async with self.session() as session:
            session.add(new_pluggy_item)
            await session.commit()

    async def create_accounts(self, accounts: list[PluggyAccountModel]) -> None:
        async with self.session() as session:
            session.add_all(accounts)
            await session.commit()

    async def create_transactions(self, transactions: list[PluggyTransactionModel]) -> None:
        async with self.session() as session:
            session.add_all(transactions)
            await session.commit()

    async def create_bills(self, bills: list[PluggyCardBillModel]) -> None:
        async with self.session() as session:
            session.add_all(bills)
            await session.commit()

    async def create_investments(self, investments: list[PluggyInvestmentModel]) -> None:
        async with self.session() as session:
            session.add_all(investments)
            await session.commit()

    async def create_investment_transactions(self, transactions: list[PluggyInvestmentTransactionModel]) -> None:
        async with self.session() as session:
            session.add_all(transactions)
            await session.commit()

    async def create_loans(self, loans: list[PluggyLoanModel]) -> None:
        async with self.session() as session:
            session.add_all(loans)
            await session.commit()

    async def get_accounts_by_user(self, user_id: uuid.UUID) -> list[PluggyAccountModel]:
        stmt = select(PluggyAccountModel).where(PluggyAccountModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_transactions_by_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> list[PluggyTransactionModel]:
        stmt = select(PluggyTransactionModel).where(
            PluggyTransactionModel.user_id == user_id,
            PluggyTransactionModel.account_id == account_id,
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_bills_by_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> list[PluggyCardBillModel]:
        stmt = select(PluggyCardBillModel).where(
            PluggyCardBillModel.user_id == user_id,
            PluggyCardBillModel.account_id == account_id,
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_investments_by_user(self, user_id: uuid.UUID) -> list[PluggyInvestmentModel]:
        stmt = select(PluggyInvestmentModel).where(PluggyInvestmentModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_investment_transactions(self, user_id: uuid.UUID, investment_id: uuid.UUID) -> list[PluggyInvestmentTransactionModel]:
        stmt = select(PluggyInvestmentTransactionModel).where(
            PluggyInvestmentTransactionModel.user_id == user_id,
            PluggyInvestmentTransactionModel.investment_id == investment_id,
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())

    async def get_loans_by_user(self, user_id: uuid.UUID) -> list[PluggyLoanModel]:
        stmt = select(PluggyLoanModel).where(PluggyLoanModel.user_id == user_id)
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return list(cursor.scalars().all())
