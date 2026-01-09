from enum import Enum
from datetime import datetime
import urllib.parse
from typing import Any, cast

from ..enum import NotionDatasourceEnum, GlobalTransactionType
from .base_template_access import BaseTemplateAccessInterface


class TransactionType(str, Enum):
    INCOME = "Entrada"
    OUTCOME = "Saída"
    TRANSFER = "Movimentação"


class EjFinanceAccess(BaseTemplateAccessInterface):
    def get_transaction_enum(self) -> type[Enum]:
        return TransactionType

    async def get_transactions(
        self,
        cursor: str | None = None,
        page_size: int | None = None,
        filter: dict[str, Any] | None = None,
        properties: list[Any] | None = None,
    ) -> dict[str, Any]:
        if properties != None:
            properties = [urllib.parse.unquote(id) for id in properties]
        data = await self.notion_external.get_datasource(
            self.datasources[NotionDatasourceEnum.TRANSACTIONS.value]["id"],
            start_cursor=cursor,
            page_size=cast(int, page_size),
            filter=filter,
            filter_properties=properties,
            sorts=[
                {
                    "property": "Data Planejada",  # TODO: remover
                    "direction": "descending",
                }
            ],
        )
        return await self.notion_external.process_datasource_registers(data)

    async def new_get_transactions(
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
        datasource_id = self.datasources[NotionDatasourceEnum.TRANSACTIONS.value]["id"]
        filter: dict[str, Any] = {"and": []}

        if name is not None:
            name_filter = {"property": "Name", "title": {"contains": name}}
            filter["and"].append(name_filter)

        if has_paid is not None:
            status_filter = {
                "property": "Status",
                "status": {"equals": "Pago" if has_paid else "Pendente"},
            }
            filter["and"].append(status_filter)

        if card_account_enter_id is not None:
            enter_in_filter = {
                "property": "Entrada em",
                "relation": {"contains": card_account_enter_id},
            }
            filter["and"].append(enter_in_filter)

        if card_account_out_id is not None:
            out_of_filter = {
                "property": "Saida de",
                "relation": {"contains": card_account_out_id},
            }
            filter["and"].append(out_of_filter)

        if category_id is not None:
            category_filter = {
                "property": "Categoria",
                "relation": {"contains": category_id},
            }
            filter["and"].append(category_filter)

        if macro_category_id is not None:
            marco_category_filter = {
                "property": "Macro Categorias",
                "relation": {"contains": macro_category_id},
            }
            filter["and"].append(marco_category_filter)

        if month_id is not None:
            month_filter = {"property": "Gestão", "relation": {"contains": month_id}}
            filter["and"].append(month_filter)

        if transaction_type is not None:
            transaction_type_filter = {
                "property": "Tipo de Transação",
                "select": {"equals": transaction_type},
            }
            filter["and"].append(transaction_type_filter)

        data = await self.notion_external.get_datasource(
            datasource_id=datasource_id,
            start_cursor=cursor,
            page_size=cast(int, page_size),
            filter=filter,
            sorts=[
                {
                    "property": "Data Planejada",  # TODO: remover
                    "direction": "descending",
                }
            ],
        )

        return await self.notion_external.process_datasource_registers(data)

    async def get_months_by_year(
        self, year: int | None, property_ids: list[str] = []
    ) -> dict[str, Any] | None:
        try:
            full_properties = await self.__get_properties(NotionDatasourceEnum.MONTHS)
            title_property_id = self.__get_title_property_from_schema(full_properties)
            property_ids_parsed = [urllib.parse.unquote(id) for id in property_ids]
            year = year or datetime.now().year
            data = await self.notion_external.get_datasource(
                self.datasources[NotionDatasourceEnum.MONTHS.value]["id"],
                filter_properties=[title_property_id, *property_ids_parsed],
                filter={
                    "and": [
                        {
                            "property": "Data Inicio",
                            "date": {"on_or_after": f"{year}"},
                        }
                    ]
                },
            )
            return await self.notion_external.process_datasource_registers(data)
        except Exception as e:
            print(e)
        return None

    async def get_current_month(self) -> dict[str, Any]:
        data = await self.notion_external.get_datasource(
            self.datasources[NotionDatasourceEnum.MONTHS.value]["id"],
            filter={
                "and": [
                    {
                        "property": "GestaoAtual",  # TODO remover
                        "formula": {"checkbox": {"equals": True}},
                    }
                ]
            },
        )
        return await self.notion_external.process_datasource_registers(data)

    async def create_out_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        card_id: str,
        category_id: str | None,
        macro_category_id: str | None,
        status: bool = True,
    ) -> dict[str, Any]:
        return await self.create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            transaction_type=GlobalTransactionType.OUTCOME,
            debit_account_id=card_id,
            category_id=category_id,
            macro_category_id=macro_category_id,
            status=status,
        )

    async def create_in_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        card_id: str,
        status: bool = True,
        hasPaid: bool = True,
    ) -> dict[str, Any]:
        return await self.create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            enter_account_id=card_id,
            status=status,
            transaction_type=GlobalTransactionType.INCOME,
        )

    async def create_transfer_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        account_id_in: str,
        account_id_out: str,
        status: bool = True,
    ) -> dict[str, Any]:
        return await self.create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            enter_account_id=account_id_in,
            debit_account_id=account_id_out,
            status=status,
            transaction_type=GlobalTransactionType.TRANSFER,
        )

    async def create_planning(
        self,
        name: str,
        month_id: str,
        category_id: str,
        amount: Any,
        text: str,
    ) -> dict[str, Any]:
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[NotionDatasourceEnum.PLANNING.value][
                    "id"
                ],
            },
            "properties": {
                "Name": {"title": [{"text": {"content": name}}]},
                "Gestão": {"relation": [{"id": month_id}]},
                "Areas e Categorias": {"relation": [{"id": category_id}]},
                "Valor planejado": {"number": amount},
                "Observações": {"rich_text": [{"text": {"content": text}}]},
            },
        }
        return await self.notion_external.create_page(page)

    async def create_card(self, name: str, initial_balance: float) -> dict[str, Any]:
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[NotionDatasourceEnum.CARDS.value][
                    "id"
                ],
            },
            "properties": {
                "Name": {"title": [{"text": {"content": name}}]},
                "Saldo Inicial": {"number": initial_balance},
            },
        }
        return await self.notion_external.create_page(page)

    async def create_month(
        self, name: str, start_date: str, finish_date: str
    ) -> dict[str, Any]:
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[NotionDatasourceEnum.MONTHS.value][
                    "id"
                ],
            },
            "properties": {
                "Name": {"title": [{"text": {"content": name}}]},
                "Data Inicio": {"date": {"start": start_date}},
                "Data Fim": {"date": {"start": finish_date}},
            },
        }
        return await self.notion_external.create_page(page)

    async def get_planning_by_month(self, month_id: str) -> dict[str, Any]:
        datasource_id = self.datasources[NotionDatasourceEnum.PLANNING.value]["id"]
        data = await self.notion_external.get_datasource(
            datasource_id,
            filter={
                "and": [
                    {
                        "property": "Gestão",  # TODO Remover
                        "relation": {"contains": month_id},
                    }
                ]
            },
        )
        return await self.notion_external.process_datasource_registers(data)

    async def get_accounts_with_balance(self) -> dict[str, Any]:
        balance_id = await self.get_property_id_from_datasource_by_property_name(
            NotionDatasourceEnum.CARDS, "Saldo Atual"
        )
        if balance_id is None:
            raise ValueError(
                "It's not possible to identify balance column. Contact admin!"
            )
        return await self.get_simple_data(
            datasource=NotionDatasourceEnum.CARDS, property_ids=[balance_id]
        )

    async def create_new_transaction(
        self,
        name: str,
        month_id: str,
        amount: float,
        date: str,
        transaction_type: GlobalTransactionType,
        enter_account_id: str | None = None,
        debit_account_id: str | None = None,
        category_id: str | None = None,
        macro_category_id: str | None = None,
        status: bool = True,
    ) -> dict[str, Any]:
        template_transaction_type = self.__convert_global_transaction_type(
            transaction_type
        )
        properties = {
            **(
                {"Name": {"title": [{"text": {"content": name}}]}}
                if name is not None
                else {}
            ),
            **(
                {"Categoria": {"relation": [{"id": category_id}]}}
                if category_id is not None
                else {}
            ),
            **(
                {"Gestão": {"relation": [{"id": month_id}]}}
                if month_id is not None
                else {}
            ),
            **(
                {"Entrada em": {"relation": [{"id": enter_account_id}]}}
                if enter_account_id is not None
                else {}
            ),
            **(
                {"Saida de": {"relation": [{"id": debit_account_id}]}}
                if debit_account_id is not None
                else {}
            ),
            **(
                {"Macro Categorias": {"relation": [{"id": macro_category_id}]}}
                if macro_category_id is not None
                else {}
            ),
            **({"Valor": {"number": amount}} if amount is not None else {}),
            **(
                {"Data Planejada": {"date": {"start": date}}}
                if date is not None
                else {}
            ),
            **(
                {
                    "Tipo de Transação": {
                        "select": {"name": template_transaction_type.value}
                    }
                }
                if template_transaction_type is not None
                else {}
            ),
            **(
                {"Status": {"status": {"name": "Pago" if status else "Pendente"}}}
                if status is not None
                else {}
            ),
        }
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[
                    NotionDatasourceEnum.TRANSACTIONS.value
                ]["id"],
            },
            "properties": properties,
        }
        return await self.notion_external.create_page(page)

    def __convert_global_transaction_type(
        self, transaction_type: GlobalTransactionType
    ) -> TransactionType:
        match transaction_type:
            case GlobalTransactionType.INCOME:
                return TransactionType.INCOME
            case GlobalTransactionType.OUTCOME:
                return TransactionType.OUTCOME
            case GlobalTransactionType.TRANSFER | GlobalTransactionType.PAY_CREDIT_CARD:
                return TransactionType.TRANSFER
