from collections.abc import Callable
from uuid import UUID
from typing import Annotated, TypeAlias, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query

from application import TransactionApplication
from dto import PaginatedDataListDto
from dto.models import TransactionDto

from .request_models.transaction import TransactionRequest, TransactionFilter

class TransactionController(APIRouter):
    """Controller exposing transaction endpoints."""

    def __init__(self, jwt_dependency: Callable[..., Any], app_dependency: Callable[[], TransactionApplication]):
        super().__init__(prefix="/transactions", dependencies=[Depends(jwt_dependency)])

        PaginatedTransactionsDto: TypeAlias = PaginatedDataListDto[TransactionDto]
        @self.get("", response_model=PaginatedTransactionsDto)
        async def get_transactions(
            request: Request,
            filter: Annotated[TransactionFilter, Query()],
            app: TransactionApplication = Depends(app_dependency)
        ) -> PaginatedTransactionsDto:
            filter.user_id = request.state.user.id
            transaction_list = await app.get_user_transactions_with_filter(filter)
            return transaction_list


        @self.post("", response_model=TransactionDto)
        async def create_transaction(
            request: Request,
            data: TransactionRequest,
            app: TransactionApplication = Depends(app_dependency),
        ) -> TransactionDto:
            data.user_id = request.state.user.id
            return cast(TransactionDto, await app.create(data))

        @self.put("/{transaction_id}")
        async def update_transaction(
            transaction_id: UUID,
            request: Request,
            data: TransactionRequest,
            app: TransactionApplication = Depends(app_dependency),
        ) -> Response:
            data.user_id = request.state.user.id
            await app.update(transaction_id, data)
            return Response(status_code=status.HTTP_201_CREATED)

        @self.delete("/{transaction_id}")
        async def delete_transaction(
            transaction_id: UUID,
            request: Request,
            app: TransactionApplication = Depends(app_dependency),
        ) -> dict[str, str]:
            await app.delete(transaction_id, request.state.user.id)
            return {"detail": "deleted"}

        @self.get("/{transaction_id}", response_model=TransactionDto)
        async def get_transaction(
            transaction_id: UUID,
            app: TransactionApplication = Depends(app_dependency),
        ) -> TransactionDto:
            trxs = await app.get_by_ids([transaction_id])
            if not trxs:
                raise HTTPException(status_code=404, detail="transaction not found")
            return cast(TransactionDto, trxs[0])
