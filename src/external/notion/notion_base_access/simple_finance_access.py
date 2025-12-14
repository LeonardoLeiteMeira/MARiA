from enum import Enum
from datetime import datetime
import urllib.parse

from ..enum import NotionDatasourceEnum
from .base_template_access import BaseTemplateAccessInterface

class TransactionType(Enum):
    INCOME = 'Entrada'
    OUTCOME = 'Saida'
    TRANSFER = 'Movimentação Interna'
    PAY_CREDIT_CARD = 'Pagar fatura cartão'

class SimpleFinanceAccess(BaseTemplateAccessInterface):
    def get_transaction_enum(self):
        return TransactionType

    async def get_transactions(self, cursor: str = None, page_size: int = None, filter: dict = None, properties: list = None) -> dict:
        if properties!= None:
            properties = [urllib.parse.unquote(id) for id in properties]
        data = await self.notion_external.get_datasource(
            self.datasources[NotionDatasourceEnum.TRANSACTIONS.value]['id'],
            start_cursor=cursor,
            page_size=page_size,
            filter=filter,
            filter_properties=properties,
            sorts=[
                {
                    "property": "Criado em",# TODO: remover
                    "direction": "descending"
                }
            ]
        )
        return await self.notion_external.process_datasource_registers(data)
    
    async def new_get_transactions(
            self,
            name: str|None,
            has_paid: bool|None,
            card_account_enter_id: str|None,
            card_account_out_id: str|None,
            category_id: str|None,
            macro_category_id: str|None,
            month_id: str|None,
            transaction_type: str|None,
            cursor: str| None,
            page_size: int
        ) -> dict:
        datasource_id = self.datasources[NotionDatasourceEnum.TRANSACTIONS.value]['id']
        filter = {"and": []}

        if name is not None:
            name_filter = {"property": "Name","title": {"contains": name}}
            filter["and"].append(name_filter)

        if card_account_enter_id is not None:
            enter_in_filter  = {"property": "Entrada em", "relation": {"contains": card_account_enter_id}}
            filter["and"].append(enter_in_filter)

        if card_account_out_id is not None:
            out_of_filter  = {"property": "Saida de", "relation": {"contains": card_account_out_id}}
            filter["and"].append(out_of_filter)

        if category_id is not None:
            category_filter  = {"property": "Categoria", "relation": {"contains": category_id}}
            filter["and"].append(category_filter)

        if macro_category_id is not None:
            marco_category_filter  = {"property": "Tipo Saida", "relation": {"contains": macro_category_id}}
            filter["and"].append(marco_category_filter)
        
        if month_id is not None:
            month_filter  = {"property": "Mês", "relation": {"contains": month_id}}
            filter["and"].append(month_filter)

        if transaction_type is not None:
            transaction_type_filter  = {"property": "Tipo Transação", "select": {"equals": transaction_type}}
            filter["and"].append(transaction_type_filter)

        data = await self.notion_external.get_datasource(
            datasource_id=datasource_id,
            start_cursor=cursor,
            page_size=page_size,
            filter=filter,
            sorts=[
                {
                    "property": "Criado em",# TODO: remover
                    "direction": "descending"
                }
            ]
        )

        return await self.notion_external.process_datasource_registers(data)

    
    async def get_months_by_year(self, year:int|None, property_ids: list[str] = []) -> dict:
        try:
            full_properties = await self.__get_properties(NotionDatasourceEnum.MONTHS)
            title_property_id = self.__get_title_property_from_schema(full_properties)
            property_ids_parsed = [urllib.parse.unquote(id) for id in property_ids]
            year = year or datetime.now().year
            data = await self.notion_external.get_datasource(
                self.datasources[NotionDatasourceEnum.MONTHS.value]['id'],
                filter_properties=[title_property_id, *property_ids_parsed],
                filter={
                    'and':[{
                        'property': 'MesData',
                            'date': {'on_or_after': f"{year}"},
                        }]}
                )
            return await self.notion_external.process_datasource_registers(data)
        except Exception as e:
            print(e)

    
    async def get_current_month(self) -> dict:
        data = await self.notion_external.get_datasource(
            self.datasources[NotionDatasourceEnum.MONTHS.value]['id'],
            filter={
                'and': [{
                'property': 'isMesAtual', # TODO remover
                'formula': {
                    'checkbox': {
                        'equals': True
                }}}]
            }    
        )
        return await self.notion_external.process_datasource_registers(data)
    
    
    async def create_out_transaction(self, name: str, month_id:str, amount: float, date:str, card_id:str, category_id:str | None, type_id:str | None, status: bool = True):
        await self.__create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            transaction_type=TransactionType.OUTCOME,
            card_id_out=card_id,
            category_id=category_id,
            type_id=type_id,
            status=status
        )
       
    async def create_in_transaction(self, name:str, month_id:str, amount:float, date:str, card_id:str, status: bool = True):
        await self.__create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            card_id_enter=card_id,
            status=status,
            transaction_type=TransactionType.INCOME,
        )

    async def create_transfer_transaction(self, name:str, month_id:str, amount:str, date:str, account_id_in:str, account_id_out:str, status: bool = True):
        await self.__create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            card_id_enter=account_id_in,
            card_id_out=account_id_out,
            status=status,
            transaction_type=TransactionType.TRANSFER,
        )

    async def create_planning(
            self,
            name,
            month_id,
            category_id,
            amount,
            text 
        ):
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[NotionDatasourceEnum.PLANNING.value]['id']
            },
            "properties": {
                "Name": {"title": [{"text": {"content": name}}]},
                "Mes": {"relation": [{"id": month_id}]},
                "Categoria": {"relation": [{"id": category_id}]},
                "Planejado": {"number": amount},
            },
        }
        await self.notion_external.create_page(page)

    async def create_card(self, name: str, initial_balance: float):
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[NotionDatasourceEnum.CARDS.value]['id']
            },
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": name}}
                    ]
                },
                "Saldo inicial": {
                    "number": initial_balance
                },
            },
        }
        await self.notion_external.create_page(page)

    async def create_month(self, name: str, start_date:str, finish_date:str):
        page = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.datasources[NotionDatasourceEnum.MONTHS.value]['id']
            },
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": name}}
                    ]
                },
                "MesData": {"date":{"start": start_date, "end": finish_date}},
            },
        }
        await self.notion_external.create_page(page)

    async def get_planning_by_month(self, month_id) -> dict:
        datasource_id = self.datasources[NotionDatasourceEnum.PLANNING.value]['id']
        data = await self.notion_external.get_datasource(
            datasource_id,
            filter={
                'and': [{
                'property': 'Mes', # TODO Remover
                'relation': {'contains':month_id}}]
            }    
        )
        return await self.notion_external.process_datasource_registers(data)
    
    async def __create_new_transaction(
            self,
            name: str,
            month_id: str,
            amount: float,
            date: str,
            transaction_type: TransactionType,
            card_id_enter: str|None = None, 
            card_id_out: str|None = None, 
            category_id: str| None = None, 
            type_id: str| None = None, 
            status: bool = True
        ):
        properties = {
            **({"Name": {"title": [{"text": {"content": name}}]}} if name is not None else {}),
            **({"Categoria": {"relation": [{"id": category_id}]}} if category_id is not None else {}),
            **({"Mês": {"relation": [{"id": month_id}]}} if month_id is not None else {}),
            **({"Entrada em": {"relation": [{"id": card_id_enter}]}} if card_id_enter is not None else {}),
            **({"Saida de": {"relation": [{"id": card_id_out}]}} if card_id_out is not None else {}),
            **({"Tipo Saida": {"relation": [{"id": type_id}]}} if type_id is not None else {}),
            **({"Valor": {"number": amount}} if amount is not None else {}),
            **({"Criado em": {"date": {"start": date}}} if date is not None else {}),
            **({"Tipo Transação": {"select": {"name": transaction_type.value}}} if transaction_type is not None else {})
        }
        page = {
            "parent": {"type": "data_source_id","data_source_id": self.datasources[NotionDatasourceEnum.TRANSACTIONS.value]['id']},
            "properties": properties,
        }
        await self.notion_external.create_page(page)
