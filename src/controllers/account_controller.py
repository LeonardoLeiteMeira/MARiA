from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from application import AccountApplication
from .request_models.account import AccountRequest
from .response_models.account import AccountResponse


class AccountController(APIRouter):
    """Controller for account CRUD operations."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], AccountApplication]):
        super().__init__(prefix="/accounts", dependencies=[Depends(jwt_dependency)])

        @self.post("/", response_model=AccountResponse)
        async def create_account(
            request: Request,
            data: AccountRequest,
            app: AccountApplication = Depends(app_dependency),
        ):
            # enforce authenticated user ownership before delegating
            data.user_id = request.state.user.id
            return await app.create(data)

        @self.put("/{account_id}", response_model=AccountResponse)
        async def update_account(
            account_id: UUID,
            request: Request,
            data: AccountRequest,
            app: AccountApplication = Depends(app_dependency),
        ):
            # ensure update targets resource owned by current user
            data.user_id = request.state.user.id
            return await app.update(account_id, data)

        @self.delete("/{account_id}")
        async def delete_account(
            account_id: UUID,
            request: Request,
            app: AccountApplication = Depends(app_dependency),
        ):
            # include user in delete to avoid removing foreign records
            await app.delete(account_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/user/{user_id}", response_model=list[AccountResponse])
        async def get_accounts_by_user(
            user_id: UUID,
            app: AccountApplication = Depends(app_dependency),
        ):
            return await app.get_by_user_id(user_id)

        @self.get("/{account_id}", response_model=AccountResponse)
        async def get_account(
            account_id: UUID,
            app: AccountApplication = Depends(app_dependency),
        ):
            accounts = await app.get_by_ids([account_id])
            if not accounts:
                raise HTTPException(status_code=404, detail="account not found")
            return accounts[0]

        @self.get("/", response_model=list[AccountResponse])
        async def get_accounts(
            ids: list[UUID] | None = Query(default=None),
            app: AccountApplication = Depends(app_dependency),
        ):
            ids = ids or []
            return await app.get_by_ids(ids)
