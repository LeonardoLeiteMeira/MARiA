from datetime import datetime, timedelta
from typing import TypedDict
import uuid

from domain import PluggyItemDomain
from repository import PluggyItemModel, PluggyAccountModel, PluggyTransactionModel
from external.pluggy import PluggyAuthLoader

import httpx

class ApiKeyControll(TypedDict):
    created_at: datetime
    key: str

class OpenFinanceApplication:
    def __init__(self, pluggy_item_domain: PluggyItemDomain, pluggy_auth_loader: PluggyAuthLoader):
        self.__pluggy_item_domain = pluggy_item_domain
        self.__pluggy_auth_loader = pluggy_auth_loader
        self.__pluggy_api_key: ApiKeyControll | None = None

    async def create_new_item(self, pluggy_item: PluggyItemModel):
        updated_pluggy_item = await self.__pluggy_item_domain.create_if_not_exist(pluggy_item)
        if not updated_pluggy_item:
            return
        
        for product in updated_pluggy_item.products:
            match (product):
                case 'ACCOUNTS':
                    await self.load_accounts(updated_pluggy_item)
                case 'INVESTMENTS':# TODO VERIFICAR SE TA ESCRITO CERTO
                    print('2')
                case 'LOANS':# TODO VERIFICAR SE TA ESCRITO CERTO
                    pass

    async def load_accounts(self, updated_pluggy_item: PluggyItemModel):
        api_key = await self.__get_api_key()
        item_id = str(updated_pluggy_item.item_id)
        accounts = []
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.pluggy.ai/accounts?itemId={item_id}", headers={"X-API-KEY": api_key})
            accounts = response.json().get("results", [])

        created_accounts = []
        for acct in accounts:
            new_account = PluggyAccountModel()
            new_account.id = uuid.uuid4()
            new_account.user_id = updated_pluggy_item.user_id
            new_account.account_id = acct['id']
            new_account.name = acct['name']
            new_account.type = acct['type']
            new_account.marketing_name = acct['marketingName']
            new_account.complementary_data = acct
            created_accounts.append(new_account)

        await self.__pluggy_item_domain.create_accounts(created_accounts)
        await self.load_transactions(created_accounts, item_id)
        # se for do tipo 'CREDIT' chamar o get credit card bills

    async def load_transactions(self, accounts: list[PluggyAccountModel], item_id: str):
        api_key = await self.__get_api_key()
        all_account_transactions = []
        for acc in accounts:
            account_id = str(acc.account_id)
            transactions = []
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.pluggy.ai/transactions?itemId={item_id}&accountId={account_id}", headers={"X-API-KEY": api_key})
                transactions = response.json().get("results", [])
            
            for transaction in transactions:
                new_transaction = PluggyTransactionModel()
                new_transaction.id = uuid.uuid4()
                new_transaction.user_id = acc.user_id
                new_transaction.user_id = acc.id
                new_transaction.pluggy_account_id = transaction['accountId']
                new_transaction.transaction_id = transaction['id']
                new_transaction.amount = transaction['amount']
                new_transaction.balance = transaction['balance']
                new_transaction.category = transaction['category']
                new_transaction.description = transaction['description']
                new_transaction.status = transaction['status']
                new_transaction.type = transaction['type']
                new_transaction.complementary_data = transaction

                all_account_transactions.append(new_transaction)

        await self.__pluggy_item_domain.create_transactions(all_account_transactions)
        


    async def load_credit_card_bills(self, accounts: list[PluggyAccountModel]):
        api_key = await self.__get_api_key()
        all_bills = []
        for acc in accounts:
            if acc.type != "CREDIT":
                continue
            account_id = str(acc.account_id)
            acc_bills = []
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.pluggy.ai/bills?accountId={account_id}", headers={"X-API-KEY": api_key})
                bills = response.json().get("results", [])

            for bill in bills:
                # Criar tabela
                # Montar objeto
                acc_bills.append({})

        
        if len(all_bills) > 0:
            #TODO: Criar metodo
            await self.__pluggy_item_domain.create_bills(all_bills)


    async def load_investiments(self):
        # https://api.pluggy.ai/investments
        # Para cada investimento carregado listar as transcoes de investimento
        # https://api.pluggy.ai/investments/{id}/transactions

        pass

    async def load_loan(self):
        # https://api.pluggy.ai/loans
        pass


    async def __get_api_key(self):
        date_now = datetime.now()
        if self.__pluggy_api_key == None or date_now - self.__pluggy_api_key['created_at'] > timedelta(minutes=30):
            api_key = await self.__pluggy_auth_loader.get_api_key()
            self.__pluggy_api_key = {
                'created_at': datetime.now(),
                'key': api_key
            }

        return self.__pluggy_api_key['key']










    # Codigo gerado pelo chat
    async def handle_webhook(self, payload: dict):
        event = payload.get("event")
        print(f"Webhook recebido: {event}")

        match event:
            case "transactions/created":
                await self.handle_transactions_created(payload)
            case "transactions/updated":
                await self.handle_transactions_updated(payload)
            case "transactions/deleted":
                await self.handle_transactions_deleted(payload)
            case "item/updated":
                print(f"Item atualizado: {payload.get('itemId')}")
            case "item/error":
                print(f"Erro ao atualizar item: {payload.get('itemId')}")
            case _:
                print(f"Evento não tratado: {event}")

    async def handle_transactions_created(self, payload: dict):
        link = payload.get("createdTransactionsLink")
        if not link:
            print("createdTransactionsLink ausente no payload")
            return

        async with httpx.AsyncClient() as client:
            response = await client.get(link, headers={"X-API-KEY": "SUA_CHAVE"})
            response.raise_for_status()
            transactions = response.json().get("results", [])

        print(f"{len(transactions)} transações criadas")
        # Salvar no banco de dados, por exemplo
        for tx in transactions:
            print(f"Nova transação: {tx['description']} R$ {tx['amount']}")

    async def handle_transactions_updated(self, payload: dict):
        tx_ids = payload.get("transactionIds", [])
        if not tx_ids:
            print("Nenhuma transação atualizada")
            return

        ids_query = ",".join(tx_ids)
        url = f"https://api.pluggy.ai/transactions?ids={ids_query}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"X-API-KEY": "SUA_CHAVE"})
            response.raise_for_status()
            updated = response.json().get("results", [])

        print(f"{len(updated)} transações atualizadas")
        for tx in updated:
            print(f"Atualizada: {tx['id']} - {tx['description']}")

    async def handle_transactions_deleted(self, payload: dict):
        tx_ids = payload.get("transactionIds", [])
        print(f"{len(tx_ids)} transações deletadas: {tx_ids}")
        # Remover do banco de dados local