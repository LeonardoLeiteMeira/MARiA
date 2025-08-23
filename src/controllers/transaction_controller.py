from collections.abc import Callable
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query

from application import TransactionApplication
from .request_models.transaction import TransactionRequest, TransactionFilter
from .response_models.transaction import TransactionResponse, TransactionListResponse


class TransactionController(APIRouter):
    """Controller exposing transaction endpoints."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], TransactionApplication]):
        super().__init__(prefix="/transactions", dependencies=[Depends(jwt_dependency)])

        @self.post("/", response_model=TransactionResponse)
        async def create_transaction(
            request: Request,
            data: TransactionRequest,
            app: TransactionApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            return await app.create(data)

        @self.put("/{transaction_id}")
        async def update_transaction(
            transaction_id: UUID,
            request: Request,
            data: TransactionRequest,
            app: TransactionApplication = Depends(app_dependency),
        ):
            data.user_id = request.state.user.id
            await app.update(transaction_id, data)
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/{transaction_id}")
        async def delete_transaction(
            transaction_id: UUID,
            request: Request,
            app: TransactionApplication = Depends(app_dependency),
        ):
            await app.delete(transaction_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/{transaction_id}", response_model=TransactionResponse)
        async def get_transaction(
            transaction_id: UUID,
            app: TransactionApplication = Depends(app_dependency),
        ):
            trxs = await app.get_by_ids([transaction_id])
            if not trxs:
                raise HTTPException(status_code=404, detail="transaction not found")
            return trxs[0]

        @self.get("/", response_model=TransactionListResponse)
        async def get_transactions(
            request: Request,
            app: TransactionApplication = Depends(app_dependency),
            filter: Annotated[TransactionFilter, Query()] = None
        ):
            filter.user_id = request.state.user.id
            trxs = await app.get_user_transactions_with_filter(filter)
            return TransactionListResponse(data=trxs)
            # Olhar o fastapi-pagination para paginacao
