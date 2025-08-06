from uuid import UUID
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class PluggyAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    marketing_name: str
    type: str
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    account_id: UUID
    amount: float
    balance: float | None
    category: str | None
    description: str
    status: str
    type: str
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyCardBillResponse(BaseModel):
    id: UUID
    account_id: UUID
    user_id: UUID
    total_amount: float
    minimum_payment_amount: float | None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyInvestmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    code: str | None
    name: str
    type: str
    subtype: str | None
    balance: float
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyInvestmentTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    investment_id: UUID
    amount: float
    value: float
    quantity: float
    type: str
    movement_type: str | None
    description: str | None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyLoanResponse(BaseModel):
    id: UUID
    user_id: UUID
    contract_number: str | None
    product_name: str
    type: str
    contract_amount: float
    currency_code: str | None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

