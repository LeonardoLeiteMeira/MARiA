from datetime import timezone, datetime

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..db_models.transaction_model import TransactionModel
    from controllers.request_models.transaction import TransactionFilter

class TransactionFilterToSqlAlchemyMixin:
    def apply_transaction_filters(
        self,
        query: Any,
        filters: 'TransactionFilter',
        Transaction: 'TransactionModel'
    ) -> Any:
        if filters.user_id is not None:
            query = query.where(Transaction.user_id == filters.user_id)

        if filters.destination_account_id:
            query = query.where(Transaction.destination_account_id.in_(filters.destination_account_id))

        if filters.source_account_id:
            query = query.where(Transaction.source_account_id.in_(filters.source_account_id))

        if filters.management_period_id:
            query = query.where(Transaction.management_period_id.in_(filters.management_period_id))

        if filters.type:
            query = query.where(Transaction.type.in_(filters.type))

        if filters.macro_category_id:
            query = query.where(Transaction.macro_category_id.in_(filters.macro_category_id))

        if filters.category_id:
            query = query.where(Transaction.category_id.in_(filters.category_id))

        if filters.tags:
            query = query.where(Transaction.tags.op("&&")(filters.tags))

        if filters.occurred_at_min is not None:
            occurred_at_min = self.__fix_time_zone(filters.occurred_at_min)
            query = query.where(Transaction.occurred_at > occurred_at_min)
        if filters.occurred_at_max is not None:
            occurred_at_max = self.__fix_time_zone(filters.occurred_at_max)
            query = query.where(Transaction.occurred_at < occurred_at_max)

        if filters.min_amount is not None:
            query = query.where(Transaction.amount_cents > filters.min_amount)
        if filters.max_amount is not None:
            query = query.where(Transaction.amount_cents < filters.max_amount)

        if filters.name:
            if getattr(filters, "str_filter", "like") == "ilike":
                query = query.where(Transaction.name.ilike(f"%{filters.name}%"))
            else:
                query = query.where(Transaction.name.like(f"%{filters.name}%"))

        if filters.sort_order:
            if filters.sort_order == 'desc':
                query = query.order_by(Transaction.occurred_at.desc())
            else:
                query = query.order_by(Transaction.occurred_at.asc())


        return query
    
    def __fix_time_zone(self, dateTime: datetime) -> datetime:
        if dateTime.tzinfo is not None:
            dateTime = dateTime.astimezone(timezone.utc).replace(tzinfo=None)
        return dateTime