from enum import Enum
from datetime import datetime
import urllib.parse

from ..enum import NotionDatabaseEnum, TransactionType
from .base_template_access import BaseTemplateAccessInterface

class EjFinanceAccess(BaseTemplateAccessInterface):
    def get_transactions(self, cursor: str = None, page_size: int = None, filter: dict = None, properties: list = None) -> dict:
        if properties!= None:
            properties = [urllib.parse.unquote(id) for id in properties]
        data = self.notion_external.get_database(
            self.databases[NotionDatabaseEnum.TRANSACTIONS.value]['id'],
            start_cursor=cursor,
            page_size=page_size,
            filter=filter,
            filter_properties=properties,
            sorts=[
                {
                    "property": "Data Planejada",# TODO: remover
                    "direction": "descending"
                }
            ]
        )
        return self.notion_external.process_database_registers(data)
    
    def new_get_transactions(
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
        database_id = self.databases[NotionDatabaseEnum.TRANSACTIONS.value]['id']
        filter = {"and": []}

        if name is not None:
            name_filter = {"property": "Name","title": {"contains": name}}
            filter["and"].append(name_filter)

        if has_paid is not None:
            status_filter  = {"property": "Status", "status": {'equals': 'Pago' if has_paid else 'Pendente'}}
            filter["and"].append(status_filter)

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
            marco_category_filter  = {"property": "Macro Categorias", "relation": {"contains": macro_category_id}}
            filter["and"].append(marco_category_filter)
        
        if month_id is not None:
            month_filter  = {"property": "Gestão", "relation": {"contains": month_id}}
            filter["and"].append(month_filter)

        if transaction_type is not None:
            transaction_type_filter  = {"property": "Tipo de Transação", "select": {"equals": transaction_type}}
            filter["and"].append(transaction_type_filter)

        data = self.notion_external.get_database(
            database_id=database_id,
            start_cursor=cursor,
            page_size=page_size,
            filter=filter,
            sorts=[
                {
                    "property": "Data Planejada",# TODO: remover
                    "direction": "descending"
                }
            ]
        )

        return self.notion_external.process_database_registers(data)

    
    def get_months_by_year(self, year:int|None, property_ids: list[str] = []) -> dict:
        try:
            full_properties = self.__get_properties(NotionDatabaseEnum.MONTHS)
            title_property_id = self.__get_title_property_from_schema(full_properties)
            property_ids_parsed = [urllib.parse.unquote(id) for id in property_ids]
            year = year or datetime.now().year
            data = self.notion_external.get_database(
                self.databases[NotionDatabaseEnum.MONTHS.value]['id'],
                filter_properties=[title_property_id, *property_ids_parsed],
                filter={
                    'and':[{
                        'property': 'Data Inicio',
                            'date': {'on_or_after': f"{year}"},
                        }]}
                )
            return self.notion_external.process_database_registers(data)
        except Exception as e:
            print(e)
    
    def get_current_month(self) -> dict:
        data = self.notion_external.get_database(
            self.databases[NotionDatabaseEnum.MONTHS.value]['id'],
            filter={
                'and': [{
                'property': 'GestaoAtual', # TODO remover
                'formula': {
                    'checkbox': {
                        'equals': True
                }}}]
            }    
        )
        return self.notion_external.process_database_registers(data)
    
    
    def create_out_transaction(self, name: str, month_id:str, amount: float, date:str, card_id:str, category_id:str, type_id:str, status: bool = True):
        self.__create_new_transaction(
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
       
    def create_in_transaction(self, name:str, month_id:str, amount:float, date:str, card_id:str, status: bool = True):
        self.__create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            card_id_enter=card_id,
            status=status,
            transaction_type=TransactionType.INCOME,
        )

    def create_transfer_transaction(self, name:str, month_id:str, amount:str, date:str, account_id_in:str, account_id_out:str, status: bool = True):
        self.__create_new_transaction(
            name=name,
            month_id=month_id,
            amount=amount,
            date=date,
            card_id_enter=account_id_in,
            card_id_out=account_id_out,
            status=status,
            transaction_type=TransactionType.TRANSFER,
        )

    def create_planning(
            self,
            name,
            month_id,
            category_id,
            amount,
            text 
        ):
        page = {
            "parent": {
                "type": "database_id",
                "database_id": self.databases[NotionDatabaseEnum.PLANNING.value]['id']
            },
            "properties": {
                "Name": {"title": [{"text": {"content": name}}]},
                "Gestão": {"relation": [{"id": month_id}]},
                "Areas e Categorias": {"relation": [{"id": category_id}]},
                "Valor planejado": {"number": amount},
                "Observações": {"rich_text": [{"text": {"content": text}}]}
            },
        }
        self.notion_external.create_page(page)

    def create_card(self, name: str, initial_balance: float):
        page = {
            "parent": {
                "type": "database_id",
                "database_id": self.databases[NotionDatabaseEnum.CARDS.value]['id']
            },
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": name}}
                    ]
                },
                "Saldo Inicial": {
                    "number": initial_balance
                },
            },
        }
        self.notion_external.create_page(page)

    def create_month(self, name: str, start_date:str, finish_date:str):
        page = {
            "parent": {
                "type": "database_id",
                "database_id": self.databases[NotionDatabaseEnum.MONTHS.value]['id']
            },
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": name}}
                    ]
                },
                "Data Inicio": {"date":{"start": start_date}},
                "Data Fim": {"date":{"start": finish_date}},
            },
        }
        self.notion_external.create_page(page)

    def get_planning_by_month(self, month_id) -> dict:
        database_id = self.databases[NotionDatabaseEnum.PLANNING.value]['id']
        data = self.notion_external.get_database(
            database_id,
            filter={
                'and': [{
                'property': 'Gestão', # TODO Remover
                'relation': {'contains':month_id}}]
            }    
        )
        return self.notion_external.process_database_registers(data)
    
    def __create_new_transaction(
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
            **({"Gestão": {"relation": [{"id": month_id}]}} if month_id is not None else {}),
            **({"Entrada em": {"relation": [{"id": card_id_enter}]}} if card_id_enter is not None else {}),
            **({"Saida de": {"relation": [{"id": card_id_out}]}} if card_id_out is not None else {}),
            **({"Macro Categorias": {"relation": [{"id": type_id}]}} if type_id is not None else {}),
            **({"Valor": {"number": amount}} if amount is not None else {}),
            **({"Data Planejada": {"date": {"start": date}}} if date is not None else {}),
            **({"Tipo de Transação": {"select": {"name": transaction_type.value}}} if transaction_type is not None else {}),
            **({'Status': {'status': {'name': 'Pago' if status else 'Pendente'}}} if status is not None else {}),
        }
        page = {
            "parent": {"type": "database_id","database_id": self.databases[NotionDatabaseEnum.TRANSACTIONS.value]['id']},
            "properties": properties,
        }
        self.notion_external.create_page(page)

