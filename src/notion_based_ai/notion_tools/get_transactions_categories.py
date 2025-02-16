from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class GetTransactionsCategoriesInput(BaseModel):
    # query: str = Field(description="should be a search query")
    pass


class GetTransactionsCategories(BaseTool):
    name: str = "get_transactions_categories"
    description: str = "List all possible categories for transactions"
    args_schema: Type[BaseModel] = GetTransactionsCategoriesInput

    def _run(self, *args, **kwargs) -> list[dict]:
        """Returns a list of all possible categories for transactions."""
        return asyncio.run(self._arun())

    async def _arun(
        self,
        *args, **kwargs
    ) -> list[dict]:
        """Returns a list of all possible categories for transactions."""
        return [
            {'id': 1, 'category': 'Alimentação'},
            {'id': 2, 'category': 'Transporte'},
            {'id': 3, 'category': 'Saúde'},
            {'id': 4, 'category': 'Educação'},
            {'id': 5, 'category': 'Entretenimento'},
            {'id': 6, 'category': 'Compras'},
            {'id': 7, 'category': 'Serviços'},
            {'id': 8, 'category': 'Investimento'},
            {'id': 9, 'category': 'Outros'}
        ]