from uuid import UUID
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class PluggyAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str | None
    marketing_name: str| None
    type: str| None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    account_id: UUID
    amount: float| None
    balance: float | None
    category: str | None
    description: str| None
    status: str| None
    type: str| None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyCardBillResponse(BaseModel):
    id: UUID
    account_id: UUID
    user_id: UUID
    total_amount: float| None
    minimum_payment_amount: float | None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyInvestmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    code: str | None
    name: str| None
    type: str| None
    subtype: str | None
    balance: float| None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyInvestmentTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    investment_id: UUID
    amount: float | None
    value: float | None
    quantity: float | None
    type: str| None
    movement_type: str | None
    description: str | None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PluggyLoanResponse(BaseModel):
    id: UUID
    user_id: UUID
    contract_number: str | None
    product_name: str | None
    type: str | None
    contract_amount: float | None
    currency_code: str | None
    complementary_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

