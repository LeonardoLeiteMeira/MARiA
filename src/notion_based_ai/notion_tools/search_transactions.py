from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class SearchTransactionsInput(BaseModel):
    # query: str = Field(description="should be a search query")
    pass


class SearchTransactions(BaseTool):
    name: str = "search_transactions"
    description: str = "Usufull when tou need to search for the latest transactions"
    args_schema: Type[BaseModel] = SearchTransactionsInput

    def _run(self, *args, **kwargs) -> list[dict]:
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        """Returns a list of more recent transactions."""
        return [
            {
                'name': 'uber',
                'amount': 20.00,
                'date': '2022-01-01',
                'card': 'Nubanck credit card',
                'category': 'Transporte'
            },
            {
                'name': 'starbucks',
                'amount': 5.75,
                'date': '2022-01-02',
                'card': 'Nubanck debit card',
                'category': 'Alimentação'
            },
            {
                'name': 'amazon',
                'amount': 50.00,
                'date': '2022-01-03',
                'card': 'Nubanck credit card',
                'category': 'Diversos'
            },
            {
                'name': 'netflix',
                'amount': 15.99,
                'date': '2022-01-04',
                'card': 'Nubanck credit card',
                'category': 'Lazer'
            },
            {
                'name': 'grocery store',
                'amount': 100.00,
                'date': '2022-01-05',
                'card': 'Nubanck debit card',
                'category': 'Alimentação'
            },
            {
                'name': 'gym membership',
                'amount': 45.00,
                'date': '2022-01-06',
                'card': 'Nubanck credit card',
                'category': 'Saúde'
            },
            {
                'name': "My girl's friend gift",
                'amount': 100.00,
                'date': '2025-02-06',
                'card': 'XP inc debit card',
                'category': 'Diversos'
            }
        ]