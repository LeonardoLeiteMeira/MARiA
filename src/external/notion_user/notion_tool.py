from datetime import datetime

from external.notion_base_access import BaseTemplateAccessInterface

class NotionTool:
    def __init__(self, template_access: BaseTemplateAccessInterface):
        self.__template_access = template_access

    async def create_income(
        self, name: str,
        month_id: str,
        amount: float,
        date: str,
        card_id: str,
        hasPaid: bool
    ):
        self.__template_access.create_in_transaction(
            name = name,
            month_id = month_id,
            amount = amount,
            date = date,
            card_id = card_id,
            hasPaid = hasPaid,
        )

    async def create_expense(self,name: str,
        month_id: str,
        amount: float,
        date: str,
        card_id: str,
        category_id: str,
        marco_category_id: str,
        hasPaid: bool
    ):
        self.__template_access.create_out_transaction(
            name,
            month_id,
            amount,
            date,
            card_id,
            category_id,
            marco_category_id,
            hasPaid
        )

    async def create_transfer(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        enter_in: str,
        out_of: str,
        hasPaid: bool
    ):
        self.__template_access.create_transfer_transaction(
            name,
            month_id,
            amount,
            date,
            enter_in,
            out_of,
            hasPaid
        )

    async def create_card(self, name: str, initial_balance: float):
        self.__template_access.create_card(name, initial_balance)

    async def create_month(self, name:str, start_date: str, finish_date: str):
        self.__template_access.create_month(
            name,
            start_date,
            finish_date
        )
        
    async def create_plan(self, 
        name: str,
        month_id: str,
        category_id: str,
        amount: str,
        text: str
    ):
        self.__template_access.create_planning(
            name,
            month_id,
            category_id,
            amount,
            text
        )

    async def delete_data(self, id: str):
        self.__template_access.delete_page(id)

    async def get_month(self, month_id: str) -> dict:
        month = self.__template_access.get_page_by_id(
            month_id,
            ['Planejamentos', 'This (Não alterar)', 'Transações']
        )
        return month
    
    async def get_plan_by_month(self, month_id) -> dict:
        return self.__template_access.get_planning_by_month(month_id)
    
    async def get_transactions(
        self, 
        name: str,
        has_paid: bool,
        card_account_enter_id: str,
        card_account_out_id: str,
        category_id: str,
        macro_category_id: str,
        month_id: str,
        transaction_type: str,
        cursor: str,
        page_size: int,
    ) -> dict:
        return self.__template_access.new_get_transactions(
            name,
            has_paid,
            card_account_enter_id,
            card_account_out_id,
            category_id,
            macro_category_id,
            month_id,
            transaction_type,
            cursor,
            page_size
        )
    
    def ger_transaction_types(self):
        return self.__template_access.get_transaction_enum()