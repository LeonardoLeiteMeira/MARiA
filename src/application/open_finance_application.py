from domain import PluggyItemDomain
from repository import PluggyItemModel

import httpx

class OpenFinanceApplication:
    def __init__(self, pluggy_item_domain: PluggyItemDomain):
        self.pluggy_item_domain = pluggy_item_domain

    async def create_new_item(self, pluggy_item: PluggyItemModel):
        updated_pluggy_item = await self.pluggy_item_domain.create_if_not_exist(pluggy_item)
        if not updated_pluggy_item:
            return

    async def load_accounts(self):
        # httpx.get(f"https://api.pluggy.ai/accounts?itemId={item_id_meuPluggy}", headers={"X-API-KEY": api_key})
        # Para cada account listar as transacoes
        pass

    async def load_credit_card_bills(self):
        # https://api.pluggy.ai/bills
        pass

    async def load_transactions(self):
        # https://api.pluggy.ai/transactions
        pass

    async def load_investiments(self):
        # https://api.pluggy.ai/investments
        # Para cada investimento carregado listar as transcoes de investimento
        # https://api.pluggy.ai/investments/{id}/transactions

        pass

    async def load_loan(self):
        # https://api.pluggy.ai/loans
        pass


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