from datetime import datetime, timedelta
from typing import TypedDict
import uuid

from domain import PluggyItemDomain
from repository import PluggyItemModel, PluggyAccountModel, PluggyTransactionModel, PluggyCardBillModel
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
                case 'INVESTMENTS':
                    pass
                case 'LOANS':
                    pass

    async def load_accounts(self, updated_pluggy_item: PluggyItemModel):
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

    async def load_transactions(self, accounts: list[PluggyAccountModel], item_id: str):
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
        


    async def load_credit_card_bills(self, accounts: list[PluggyAccountModel]):
        api_key = await self.__get_api_key()
        all_bills = []
        for acc in accounts:
            if acc.type != "CREDIT":
                continue
            account_id = str(acc.id)
            acc_bills = []
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.pluggy.ai/bills?accountId={account_id}", headers={"X-API-KEY": api_key})
                bills = response.json().get("results", [])

            for bill in bills:
                bill_model = PluggyCardBillModel()
                bill_model.id = bill['id']
                bill_model.account_id = account_id
                bill_model.user_id = acc.user_id
                bill_model.total_amount = bill['totalAmount']
                bill_model.minimum_payment_amount = bill['minimumPaymentAmount']
                bill_model.complementary_data = bill

                acc_bills.append(bill)

        
        if len(all_bills) > 0:
            await self.__pluggy_item_domain.create_bills(all_bills)


    async def load_investiments(self):
        # https://api.pluggy.ai/investments?itemId={item_id}
        # Para cada investimento carregado listar as transcoes de investimento
        # Exemplo de response
        # {
        #     "page": 1,
        #     "total": 3,
        #     "totalPages": 1,
        #     "results": [
        #         {
        #         "id": "f77eccf4-7714-498e-92a9-1bebe70335d9",
        #         "code": "12.345.678/0001-00",
        #         "name": "Bahia AM Advisory FIC de FIM",
        #         "balance": 1359.39,
        #         "currencyCode": "BRL",
        #         "type": "MUTUAL_FUND",
        #         "subtype": "MULTIMARKET_FUND",
        #         "lastMonthRate": 0.24,
        #         "annualRate": 3.24,
        #         "lastTwelveMonthsRate": 3,
        #         "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
        #         "value": 500,
        #         "quantity": 3,
        #         "amount": 1500,
        #         "taxes": 40.61,
        #         "taxes2": 100,
        #         "date": "2020-07-19T18:27:41.802Z",
        #         "owner": "John Doe",
        #         "number": null,
        #         "amountProfit": 310.5,
        #         "amountWithdrawal": 1310.5,
        #         "amountOriginal": 1000,
        #         "status": "ACTIVE",
        #         "transactions": [
        #             {
        #             "tradeDate": "2020-10-01T00:00:00.000Z",
        #             "date": "2020-10-01T00:00:00.000Z",
        #             "description": "Aplicação Fondo de Investimento Premium",
        #             "quantity": 1.25,
        #             "value": 2,
        #             "amount": 5,
        #             "type": "BUY",
        #             "movementType": "CREDIT"
        #             }
        #         ]
        #         },
        #         {
        #         "id": "2a96b873-53bb-4d16-a3d8-385a57e78d7e",
        #         "number": null,
        #         "name": "CDB1194KL0Z - BANCO MAXIMA S/A",
        #         "balance": 2000,
        #         "currencyCode": "BRL",
        #         "type": "FIXED_INCOME",
        #         "subtype": "CDB",
        #         "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
        #         "code": "0001-02",
        #         "amount": 2500,
        #         "taxes": null,
        #         "taxes2": null,
        #         "date": "2020-07-19T18:27:41.802Z",
        #         "owner": "John Doe",
        #         "rate": 30,
        #         "rateType": "CDI",
        #         "fixedAnnualRate": 10.5,
        #         "amountProfit": null,
        #         "amountWithdrawal": 2000,
        #         "amountOriginal": 1000,
        #         "issuer": "Pluggy",
        #         "issuerCNPJ": "08.050.608/0001-32",
        #         "issueDate": "2020-07-19T18:27:41.802Z",
        #         "status": "ACTIVE"
        #         },
        #         {
        #         "id": "ded7d2f1-6b90-44a8-9ace-de747b9f5bfe",
        #         "number": "123456-2",
        #         "name": "Pluggy PREVIDENCIA",
        #         "balance": 1359.39,
        #         "currencyCode": "BRL",
        #         "type": "SECURITY",
        #         "subtype": "RETIREMENT",
        #         "annualRate": 3.24,
        #         "itemId": "207f5bcd-312a-439c-abbe-166b6632c980",
        #         "code": null,
        #         "value": 500,
        #         "quantity": 3,
        #         "amount": 1500,
        #         "taxes": 0,
        #         "taxes2": 0,
        #         "date": "2020-07-19T18:27:41.802Z",
        #         "owner": "John Doe",
        #         "amountProfit": 359.39,
        #         "amountWithdrawal": 1310.5,
        #         "status": "ACTIVE",
        #         "institution": {
        #             "name": "BANCO BTG PACTUAL S/A",
        #             "number": "30306294000145"
        #         }
        #         }
        #     ]
        # }
        pass

    async def load_investiments_transactions(self):
        # https://api.pluggy.ai/investments/{id}/transactions
        # Esse id do parametro e o id do investimento carregado
        # Exemplo de response
        # {
        #     "total": 2,
        #     "totalPages": 1,
        #     "page": 1,
        #     "results": [
        #         {
        #         "id": "910419d2-e833-41f2-af43-080693f7ef8a",
        #         "amount": 60000,
        #         "description": null,
        #         "value": 1200,
        #         "quantity": 50,
        #         "tradeDate": "2021-09-15T00:00:00.000Z",
        #         "date": "2021-09-15T00:00:00.000Z",
        #         "type": "SELL",
        #         "movementType": "DEBIT",
        #         "netAmount": null,
        #         "agreedRate": null,
        #         "brokerageNumber": null,
        #         "expenses": {}
        #         },
        #         {
        #         "id": "f24f7eec-5a5b-4e54-8727-d40b0b91115a",
        #         "amount": 110000,
        #         "description": null,
        #         "value": 1100,
        #         "quantity": 100,
        #         "tradeDate": "2021-09-01T00:00:00.000Z",
        #         "date": "2021-09-01T00:00:00.000Z",
        #         "type": "BUY",
        #         "movementType": "CREDIT",
        #         "netAmount": 10000,
        #         "agreedRate": null,
        #         "brokerageNumber": "1234",
        #         "expenses": {}
        #         }
        #     ]
        # }
        pass

    async def load_loan(self):
        # https://api.pluggy.ai/loans?itemId={item_id}
        # Exemplo de response
        # {
        #     "page": 1,
        #     "total": 1,
        #     "totalPages": 1,
        #     "results": [
        #         {
        #         "id": "05c693bf-c196-47ea-a28c-8251d6bb8a06",
        #         "itemId": "5e9f8f8f-f8f8-4f8f-8f8f-8f8f8f8f8f8f",
        #         "contractNumber": "000000721792794",
        #         "ipocCode": "92792126019929279212650822221989319252576",
        #         "productName": "Crédito Pessoal Consignado",
        #         "type": "CREDITO_PESSOAL_COM_CONSIGNACAO",
        #         "date": "2023-07-20T00:00:00",
        #         "contractDate": "2022-08-01T00:00:00",
        #         "disbursementDates": [
        #             "2018-01-15T00:00:00"
        #         ],
        #         "settlementDate": "2018-01-15T00:00:00",
        #         "contractAmount": 50000,
        #         "currencyCode": "BRL",
        #         "dueDate": "2028-01-15T00:00:00",
        #         "installmentPeriodicity": "MONTHLY",
        #         "installmentPeriodicityAdditionalInfo": "",
        #         "firstInstallmentDueDate": "2018-02-15T00:00:00",
        #         "CET": 0.29,
        #         "amortizationScheduled": "SAC",
        #         "amortizationScheduledAdditionalInfo": "",
        #         "cnpjConsignee": "60.500.998/0001-35",
        #         "interestRates": [
        #             {
        #             "taxType": "EFETIVA",
        #             "interestRateType": "SIMPLES",
        #             "taxPeriodicity": "AA",
        #             "calculation": "21/252",
        #             "referentialRateIndexerType": "PRE_FIXADO",
        #             "referentialRateIndexerSubType": "TJLP",
        #             "referentialRateIndexerAdditionalInfo": "",
        #             "preFixedRate": 0.6,
        #             "postFixedRate": 0.55,
        #             "additionalInfo": ""
        #             }
        #         ],
        #         "contractedFees": [
        #             {
        #             "name": "Renovação de cadastro",
        #             "code": "CADASTRO",
        #             "chargeType": "UNICA",
        #             "charge": "MINIMO",
        #             "amount": 100000.04,
        #             "rate": 0.062
        #             }
        #         ],
        #         "contractedFinanceCharges": [
        #             {
        #             "type": "JUROS_REMUNERATORIOS_POR_ATRASO",
        #             "chargeAdditionalInfo": "",
        #             "chargeRate": 0.07
        #             }
        #         ],
        #         "warranties": [
        #             {
        #             "currencyCode": "BRL",
        #             "type": "CESSAO_DIREITOS_CREDITORIOS",
        #             "subtype": "NOTAS_PROMISSORIAS_OUTROS_DIREITOS_CREDITO",
        #             "amount": 1000.04
        #             }
        #         ],
        #         "installments": {
        #             "typeNumberOfInstallments": "MES",
        #             "totalNumberOfInstallments": 130632,
        #             "typeContractRemaining": "DIA",
        #             "contractRemainingNumber": 14600,
        #             "paidInstallments": 73,
        #             "dueInstallments": 57,
        #             "pastDueInstallments": 73,
        #             "balloonPayments": [
        #             {
        #                 "dueDate": "2021-05-21T00:00:00",
        #                 "amount": {
        #                 "value": 1000.04,
        #                 "currencyCode": "BRL"
        #                 }
        #             }
        #             ]
        #         },
        #         "payments": {
        #             "contractOutstandingBalance": 1000.04,
        #             "releases": [
        #             {
        #                 "isOverParcelPayment": true,
        #                 "installmentId": "WGx0aExYcEJMVm93TFRsZFcyRXRla0V0V2pBdE9Wd3RYWH",
        #                 "paidDate": "2021-05-21T00:00:00",
        #                 "currencyCode": "BRL",
        #                 "paidAmount": 1000.04,
        #                 "overParcel": {
        #                 "fees": [
        #                     {
        #                     "name": "Reavaliação periódica do bem",
        #                     "code": "aval_bem",
        #                     "amount": 100000.04
        #                     }
        #                 ],
        #                 "charges": [
        #                     {
        #                     "type": "JUROS_REMUNERATORIOS_POR_ATRASO",
        #                     "additionalInfo": "",
        #                     "amount": 1000.04
        #                     }
        #                 ]
        #                 }
        #             }
        #             ]
        #         }
        #         }
        #     ]
        # }
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


