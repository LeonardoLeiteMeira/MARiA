from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from typing import Annotated

from application import AccountApplication
from .request_models.account import AccountRequest
from .response_models.account import AccountResponse, AccountListResponse


class AccountController(APIRouter):
    """Controller for account CRUD operations."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], AccountApplication]):
        super().__init__(prefix="/accounts", dependencies=[Depends(jwt_dependency)])

        @self.post("", response_model=AccountResponse)
        async def create_account(
            request: Request,
            data: AccountRequest,
            app: AccountApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            return await app.create(data)

        @self.put("/{account_id}")
        async def update_account(
            account_id: UUID,
            request: Request,
            data: AccountRequest,
            app: AccountApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            await app.update(account_id, data)
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/{account_id}")
        async def delete_account(
            account_id: UUID,
            request: Request,
            app: AccountApplication = Depends(app_dependency),
        ):
            await app.delete(account_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("", response_model=list[AccountResponse])
        async def get_accounts_by_user(
            request: Request,
            app: AccountApplication = Depends(app_dependency),
        ):
            accounts = await app.get_by_user_id(request.state.user.id)
            return accounts

        @self.get("/{account_id}", response_model=AccountResponse)
        async def get_account(
            account_id: UUID,
            app: AccountApplication = Depends(app_dependency)
        ):
            accounts = await app.get_by_ids([account_id])
            if not accounts:
                raise HTTPException(status_code=404, detail="account not found")
            return accounts[0]
