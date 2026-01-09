from datetime import datetime, timedelta
from typing import Any, TypedDict, cast
import uuid

from domain import PluggyItemDomain
from repository import (
    PluggyItemModel,
    PluggyAccountModel,
    PluggyTransactionModel,
    PluggyCardBillModel,
    PluggyInvestmentModel,
    PluggyInvestmentTransactionModel,
    PluggyLoanModel,
)
from external.pluggy import PluggyAuthLoader

import httpx

class ApiKeyControll(TypedDict):
    created_at: datetime
    key: str

class OpenFinanceApplication:
    def __init__(self, pluggy_item_domain: PluggyItemDomain, pluggy_auth_loader: PluggyAuthLoader) -> None:
        self.__pluggy_item_domain = pluggy_item_domain
        self.__pluggy_auth_loader = pluggy_auth_loader
        self.__pluggy_api_key: ApiKeyControll | None = None

    async def create_new_item(self, pluggy_item: PluggyItemModel) -> None:
        updated_pluggy_item = await self.__pluggy_item_domain.create_if_not_exist(pluggy_item)
        if not updated_pluggy_item:
            return
        
        for product in updated_pluggy_item.products:
            match (product):
                case 'ACCOUNTS':
                    await self.load_accounts(updated_pluggy_item)
                case 'INVESTMENTS':
                    await self.load_investiments(updated_pluggy_item)
                case 'LOANS':
                    await self.load_loan(updated_pluggy_item)

    async def load_accounts(self, updated_pluggy_item: PluggyItemModel) -> None:
        api_key = await self.__get_api_key()
        item_id = str(updated_pluggy_item.id)
        accounts = []
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.pluggy.ai/accounts?itemId={item_id}", headers={"X-API-KEY": api_key})
            accounts = response.json().get("results", [])

        created_accounts = []
        for acct in accounts:
            new_account = PluggyAccountModel()
            new_account.id = acct['id']
            new_account.user_id = updated_pluggy_item.user_id
            new_account.name = acct['name']
            new_account.type = acct['type']
            new_account.marketing_name = acct['marketingName']
            new_account.complementary_data = acct
            created_accounts.append(new_account)

        await self.__pluggy_item_domain.create_accounts(created_accounts)
        await self.load_transactions(created_accounts, item_id)
        await self.load_credit_card_bills(created_accounts)

    async def load_transactions(self, accounts: list[PluggyAccountModel], item_id: str) -> None:
        api_key = await self.__get_api_key()
        all_account_transactions = []
        for acc in accounts:
            account_id = str(acc.id)
            transactions = []
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.pluggy.ai/transactions?itemId={item_id}&accountId={account_id}", headers={"X-API-KEY": api_key})
                transactions = response.json().get("results", [])
            
            for transaction in transactions:
                new_transaction = PluggyTransactionModel()
                new_transaction.id = transaction['id']
                new_transaction.user_id = acc.user_id
                new_transaction.account_id = acc.id
                new_transaction.amount = transaction['amount']
                new_transaction.balance = transaction['balance']
                new_transaction.category = transaction['category']
                new_transaction.description = transaction['description']
                new_transaction.status = transaction['status']
                new_transaction.type = transaction['type']
                new_transaction.complementary_data = transaction

                all_account_transactions.append(new_transaction)

        await self.__pluggy_item_domain.create_transactions(all_account_transactions)
        


    async def load_credit_card_bills(self, accounts: list[PluggyAccountModel]) -> None:
        api_key = await self.__get_api_key()
        all_bills = []
        for acc in accounts:
            if acc.type != "CREDIT":
                continue
            account_id = str(acc.id)
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.pluggy.ai/bills?accountId={account_id}", headers={"X-API-KEY": api_key})
                bills = response.json().get("results", [])

            for bill in bills:
                bill_model = PluggyCardBillModel()
                bill_model.id = bill['id']
                bill_model.account_id = cast(uuid.UUID, account_id)
                bill_model.user_id = acc.user_id
                bill_model.total_amount = bill['totalAmount']
                bill_model.minimum_payment_amount = bill['minimumPaymentAmount']
                bill_model.complementary_data = bill

                all_bills.append(bill_model)

        
        if len(all_bills) > 0:
            await self.__pluggy_item_domain.create_bills(all_bills)


    async def load_investiments(self, updated_pluggy_item: PluggyItemModel) -> None:
        api_key = await self.__get_api_key()
        item_id = str(updated_pluggy_item.id)
        investments_data = []
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.pluggy.ai/investments?itemId={item_id}",
                headers={"X-API-KEY": api_key},
            )
            investments_data = response.json().get("results", [])

        investments: list[PluggyInvestmentModel] = []
        for inv in investments_data:
            inv_model = PluggyInvestmentModel()
            inv_model.id = inv["id"]
            inv_model.user_id = updated_pluggy_item.user_id
            inv_model.code = inv["code"]
            inv_model.name = inv["name"]
            inv_model.type = inv["type"]
            inv_model.subtype = inv["subtype"]
            inv_model.balance = inv["balance"]
            inv_model.complementary_data = inv
            investments.append(inv_model)

        if investments:
            await self.__pluggy_item_domain.create_investments(investments)
            await self.load_investiments_transactions(investments)

    async def load_investiments_transactions(self, investments: list[PluggyInvestmentModel]) -> None:
        api_key = await self.__get_api_key()
        all_transactions: list[PluggyInvestmentTransactionModel] = []
        for inv in investments:
            inv_id = str(inv.id)
            transactions = []
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.pluggy.ai/investments/{inv_id}/transactions",
                    headers={"X-API-KEY": api_key},
                )
                transactions = response.json().get("results", [])

            for trx in transactions:
                trx_model = PluggyInvestmentTransactionModel()
                trx_model.id = trx["id"]
                trx_model.user_id = inv.user_id
                trx_model.investment_id = inv.id
                trx_model.amount = trx["amount"]
                trx_model.value = trx["value"]
                trx_model.quantity = trx["quantity"]
                trx_model.type = trx["type"]
                trx_model.movement_type = trx["movementType"]
                trx_model.description = trx["description"]
                trx_model.complementary_data = trx
                all_transactions.append(trx_model)

        if all_transactions:
            await self.__pluggy_item_domain.create_investment_transactions(all_transactions)

    async def load_loan(self, updated_pluggy_item: PluggyItemModel) -> None:
        api_key = await self.__get_api_key()
        item_id = str(updated_pluggy_item.id)
        loans_data = []
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.pluggy.ai/loans?itemId={item_id}",
                headers={"X-API-KEY": api_key},
            )
            loans_data = response.json().get("results", [])

        loans: list[PluggyLoanModel] = []
        for loan in loans_data:
            loan_model = PluggyLoanModel()
            loan_model.id = loan["id"]
            loan_model.user_id = updated_pluggy_item.user_id
            loan_model.contract_number = loan.get("contractNumber")
            loan_model.product_name = loan.get("productName")
            loan_model.type = loan.get("type")
            loan_model.contract_amount = loan.get("contractAmount", 0)
            loan_model.currency_code = loan.get("currencyCode")
            loan_model.complementary_data = loan
            loans.append(loan_model)

        if loans:
            await self.__pluggy_item_domain.create_loans(loans)


    async def get_accounts(self, user_id: uuid.UUID) -> list[PluggyAccountModel]:
        return await self.__pluggy_item_domain.get_accounts(user_id)

    async def get_account_transactions(self, user_id: uuid.UUID, account_id: uuid.UUID) -> list[PluggyTransactionModel]:
        return await self.__pluggy_item_domain.get_transactions(user_id, account_id)

    async def get_card_bills(self, user_id: uuid.UUID, account_id: uuid.UUID) -> list[PluggyCardBillModel]:
        return await self.__pluggy_item_domain.get_bills(user_id, account_id)

    async def get_investments(self, user_id: uuid.UUID) -> list[PluggyInvestmentModel]:
        return await self.__pluggy_item_domain.get_investments(user_id)

    async def get_investment_transactions(self, user_id: uuid.UUID, investment_id: uuid.UUID) -> list[PluggyInvestmentTransactionModel]:
        return await self.__pluggy_item_domain.get_investment_transactions(user_id, investment_id)

    async def get_loans(self, user_id: uuid.UUID) -> list[PluggyLoanModel]:
        return await self.__pluggy_item_domain.get_loans(user_id)

    async def __get_api_key(self) -> str:
        date_now = datetime.now()
        if self.__pluggy_api_key == None or date_now - self.__pluggy_api_key['created_at'] > timedelta(minutes=30):
            api_key = cast(str, await self.__pluggy_auth_loader.get_api_key())
            self.__pluggy_api_key = {
                'created_at': datetime.now(),
                'key': api_key
            }

        return self.__pluggy_api_key['key']










    # Codigo gerado pelo chat
    async def handle_webhook(self, payload: dict[str, Any]) -> None:
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

    async def handle_transactions_created(self, payload: dict[str, Any]) -> None:
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

    async def handle_transactions_updated(self, payload: dict[str, Any]) -> None:
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

    async def handle_transactions_deleted(self, payload: dict[str, Any]) -> None:
        tx_ids = payload.get("transactionIds", [])
        print(f"{len(tx_ids)} transações deletadas: {tx_ids}")
        # Remover do banco de dados local

