from .base_repository import BaseRepository
from .db_models.pluggy_item_model import PluggyItemModel
from .db_models.pluggy_account_model import PluggyAccountModel
from .db_models.pluggy_transactions_model import PluggyTransactionModel
from .db_models.pluggy_card_bill_model import PluggyCardBillModel
from .db_models.pluggy_investment_model import PluggyInvestmentModel
from .db_models.pluggy_investment_transaction_model import PluggyInvestmentTransactionModel
from .db_models.pluggy_loan_model import PluggyLoanModel

from sqlalchemy import text, Column, String, Integer, select, update, delete, desc

class PluggyItemRepository(BaseRepository):
    async def get_pluggy_item_by_item_id(self, item_id: str) -> PluggyItemModel | None:
        stmt = (
            select(PluggyItemModel)
            .where(PluggyItemModel.item_id == item_id) 
            .execution_options(synchronize_session="fetch")
        )
        async with self.session() as session:
            cursor = await session.execute(stmt)
            return cursor.scalars().first()
        
    async def create_pluggy_item(self, new_pluggy_item: PluggyItemModel):
        async with self.session() as session:
            session.add(new_pluggy_item)
            await session.commit()

    async def create_accounts(self, accounts: list[PluggyAccountModel]):
        async with self.session() as session:
            session.add_all(accounts)
            await session.commit()

    async def create_transactions(self, transactions: list[PluggyTransactionModel]):
        async with self.session() as session:
            session.add_all(transactions)
            await session.commit()

    async def create_bills(self, bills: list[PluggyCardBillModel]):
        async with self.session() as session:
            session.add_all(bills)
            await session.commit()

    async def create_investments(self, investments: list[PluggyInvestmentModel]):
        async with self.session() as session:
            session.add_all(investments)
            await session.commit()

    async def create_investment_transactions(self, transactions: list[PluggyInvestmentTransactionModel]):
        async with self.session() as session:
            session.add_all(transactions)
            await session.commit()

    async def create_loans(self, loans: list[PluggyLoanModel]):
        async with self.session() as session:
            session.add_all(loans)
            await session.commit()