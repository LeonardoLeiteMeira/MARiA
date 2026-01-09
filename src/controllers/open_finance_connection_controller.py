from collections.abc import Callable
from uuid import UUID
from typing import Any, cast

from fastapi import APIRouter, Request, Depends, Body

from external.pluggy import PluggyAuthLoader
from repository import PluggyItemModel
from application import OpenFinanceApplication
from .response_models.open_finance_connection import (
    PluggyAccountResponse,
    PluggyTransactionResponse,
    PluggyCardBillResponse,
    PluggyInvestmentResponse,
    PluggyInvestmentTransactionResponse,
    PluggyLoanResponse,
)

class OpenFinanceConnectionController(APIRouter):
    def __init__(
        self,
        jwt_dependency: Callable[..., Any],
        pluggy_auth_dependency: Callable[..., Any],
        open_finance_app: Callable[..., Any],
    ):
        super().__init__(
            prefix='/open-finance',
            dependencies=[Depends(jwt_dependency)]
        )

        @self.post("/connect-token")
        async def get_connect_token(
            request: Request,
            pluggy_auth_loader: PluggyAuthLoader = Depends(pluggy_auth_dependency),
        ) -> dict[str, Any] | None:
            user = request.state.user
            connect_token = await pluggy_auth_loader.get_connect_token(
                webhook_url="https://maria_pluggy_test.requestcatcher.com/pluggy",
                client_user_id=str(user.id)
            )
            return connect_token
            
        @self.post("/webhook")
        async def webhook() -> None:
            return None

        @self.post("/item-from-widget")
        async def receive_item_from_widget(
            request: Request,
            item_data: dict[str, Any] = Body(...),
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> None:
            user = request.state.user
            pluggy_item = PluggyItemModel.from_request_body(item_data, str(user.id))
            await open_finance_app.create_new_item(pluggy_item)

        @self.get("/accounts", response_model=list[PluggyAccountResponse])
        async def get_accounts(
            request: Request,
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> list[PluggyAccountResponse]:
            user = request.state.user
            return cast(list[PluggyAccountResponse], await open_finance_app.get_accounts(user.id))

        @self.get("/accounts/{account_id}/transactions", response_model=list[PluggyTransactionResponse])
        async def get_account_transactions(
            request: Request,
            account_id: UUID,
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> list[PluggyTransactionResponse]:
            user = request.state.user
            return cast(list[PluggyTransactionResponse], await open_finance_app.get_account_transactions(user.id, account_id))

        @self.get("/accounts/{account_id}/bills", response_model=list[PluggyCardBillResponse])
        async def get_card_bills(
            request: Request,
            account_id: UUID,
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> list[PluggyCardBillResponse]:
            user = request.state.user
            return cast(list[PluggyCardBillResponse], await open_finance_app.get_card_bills(user.id, account_id))

        @self.get("/investments", response_model=list[PluggyInvestmentResponse])
        async def get_investments(
            request: Request,
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> list[PluggyInvestmentResponse]:
            user = request.state.user
            return cast(list[PluggyInvestmentResponse], await open_finance_app.get_investments(user.id))

        @self.get("/investments/{investment_id}/transactions", response_model=list[PluggyInvestmentTransactionResponse])
        async def get_investment_transactions(
            request: Request,
            investment_id: UUID,
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> list[PluggyInvestmentTransactionResponse]:
            user = request.state.user
            return cast(list[PluggyInvestmentTransactionResponse], await open_finance_app.get_investment_transactions(user.id, investment_id))

        @self.get("/loans", response_model=list[PluggyLoanResponse])
        async def get_loans(
            request: Request,
            open_finance_app: OpenFinanceApplication = Depends(open_finance_app),
        ) -> list[PluggyLoanResponse]:
            user = request.state.user
            return cast(list[PluggyLoanResponse], await open_finance_app.get_loans(user.id))
        
