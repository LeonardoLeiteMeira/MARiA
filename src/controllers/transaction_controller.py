from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from application import TransactionApplication
from .request_models.transaction import TransactionRequest
from .response_models.transaction import TransactionResponse


class TransactionController(APIRouter):
    """Controller exposing transaction endpoints."""

    def __init__(self, jwt_dependency: Callable, app_dependency: Callable[[], TransactionApplication]):
        super().__init__(prefix="/transactions", dependencies=[Depends(jwt_dependency)])

        @self.post("/", response_model=TransactionResponse)
        async def create_transaction(
            data: TransactionRequest,
            app: TransactionApplication = Depends(app_dependency),
        ):
            return await app.create(data)

        @self.put("/{transaction_id}", response_model=TransactionResponse)
        async def update_transaction(
            transaction_id: UUID,
            data: TransactionRequest,
            app: TransactionApplication = Depends(app_dependency),
        ):
            return await app.update(transaction_id, data)

        @self.delete("/{transaction_id}")
        async def delete_transaction(
            transaction_id: UUID,
            app: TransactionApplication = Depends(app_dependency),
        ):
            await app.delete(transaction_id)
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

        @self.get("/", response_model=list[TransactionResponse])
        async def get_transactions(
            ids: list[UUID] | None = Query(default=None),
            app: TransactionApplication = Depends(app_dependency),
        ):
            ids = ids or []
            return await app.get_by_ids(ids)
