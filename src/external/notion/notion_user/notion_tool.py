from enum import Enum
from typing import Any, cast

from ..enum import GlobalTransactionType
from ..notion_base_access import BaseTemplateAccessInterface


class NotionTool:
    def __init__(self, template_access: BaseTemplateAccessInterface) -> None:
        self.__template_access = template_access

    async def create_income(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        card_id: str,
        hasPaid: bool = True,
    ) -> dict[str, Any]:
        return await self.__template_access.create_in_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            card_id=card_id,
            status=hasPaid,
        )

    async def create_new_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        enter_account_id: str | None,
        debit_account_id: str | None,
        category_id: str | None,
        macro_category_id: str | None,
        transaction_type: GlobalTransactionType,
        hasPaid: bool,
    ) -> dict[str, Any]:
        return await self.__template_access.create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            transaction_type=transaction_type,
            enter_account_id=enter_account_id,
            debit_account_id=debit_account_id,
            category_id=category_id,
            macro_category_id=macro_category_id,
            status=hasPaid,
        )

    async def create_expense(
        self,
        name: str,
        month_id: str | None,
        amount: float,
        date: str,
        card_id: str | None,
        category_id: str | None,
        marco_category_id: str | None,
        hasPaid: bool,
    ) -> dict[str, Any]:
        return await self.__template_access.create_out_transaction(
            name,
            cast(str, month_id),
            amount,
            date,
            cast(str, card_id),
            category_id,
            marco_category_id,
            hasPaid,
        )

    async def create_transfer(
        self,
        name: str,
        month_id: str | None,
        amount: float,
        date: str,
        enter_in: str | None,
        out_of: str | None,
        hasPaid: bool,
    ) -> dict[str, Any]:
        return await self.__template_access.create_transfer_transaction(
            name,
            cast(str, month_id),
            amount,
            date,
            cast(str, enter_in),
            cast(str, out_of),
            hasPaid,
        )

    async def create_card(self, name: str, initial_balance: float) -> dict[str, Any]:
        return await self.__template_access.create_card(name, initial_balance)

    async def create_month(
        self, name: str, start_date: str, finish_date: str
    ) -> dict[str, Any]:
        return await self.__template_access.create_month(name, start_date, finish_date)

    async def create_plan(
        self, name: str, month_id: str, category_id: str, amount: Any, text: str
    ) -> dict[str, Any]:
        return await self.__template_access.create_planning(
            name, month_id, category_id, amount, text
        )

    async def delete_data(self, id: str) -> None:
        await self.__template_access.delete_page(id)

    async def get_month(self, month_id: str) -> dict[str, Any]:
        return await self.__template_access.get_page_by_id(
            month_id, ["Planejamentos", "This (Não alterar)", "Transações"]
        )

    async def get_plan_by_month(self, month_id: str) -> dict[str, Any]:
        return await self.__template_access.get_planning_by_month(month_id)

    async def get_transactions(
        self,
        name: str | None,
        has_paid: bool | None,
        card_account_enter_id: str | None,
        card_account_out_id: str | None,
        category_id: str | None,
        macro_category_id: str | None,
        month_id: str | None,
        transaction_type: str | None,
        cursor: str | None,
        page_size: int | None,
    ) -> dict[str, Any]:
        return await self.__template_access.new_get_transactions(
            name,
            has_paid,
            card_account_enter_id,
            card_account_out_id,
            category_id,
            macro_category_id,
            month_id,
            transaction_type,
            cursor,
            page_size,
        )

    def ger_transaction_types(self) -> type[Enum]:
        return self.__template_access.get_transaction_enum()

    async def get_accounts_with_balance(self) -> dict[str, Any]:
        return await self.__template_access.get_accounts_with_balance()
