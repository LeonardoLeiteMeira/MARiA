from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type
import asyncio

class CreateNewTransactionInput(BaseModel):
    name: str = Field(description="Name choosen by the user to identify the transaction")
    amount: float = Field(description="Amount of the transaction")
    date: str = Field(description="Date of the transaction")
    card: str = Field(description="Id of a Card used for the transaction")
    category: str = Field(description="Id of a valid Categotry to classify the transaction")
    month: str = Field(description="Id of a Valid Month to classify the transaction")
    type: str = Field(description="Id of a valid Type to classify the transaction")


class CreateNewTransaction(BaseTool):
    name: str = "create_new_transaction"
    description: str = "Creates a new transaction with the given data - If user does not provide any parameter, it's necessary to ask."
    args_schema: Type[BaseModel] = CreateNewTransactionInput

    def _run(
        self, 
        name: str,
        amount: float,
        date: str,
        card: str,
        category: str,
        *args, **kwargs
    ) -> list[dict]:
        """Creates a new transaction with the given data - If user does not provide any parameter, it's necessary to ask."""
        return asyncio.run(self._arun(
            name,
            amount,
            date,
            card,
            category
        ))

    async def _arun(
        self,
        name: str,
        amount: float,
        date: str,
        card: str,
        category: str,
        *args, **kwargs
    ) -> list[dict]:
        """Creates a new transaction with the given data - If user does not provide any parameter, it's necessary to ask."""
        print({
            'name': name,
            'amount': amount,
            'date': date,
            'card': card,
            'category': category
        })