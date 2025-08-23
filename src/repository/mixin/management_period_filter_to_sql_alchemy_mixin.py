from datetime import timezone, datetime

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ..db_models.management_period_model import ManagementPeriodModel
    from controllers.request_models.management_period import ManagementPeriodFilter

class ManagementPeriodFilterToSqlAlchemyMixin:
    def apply_transaction_filters(
        self,
        query: Any,
        filters: 'ManagementPeriodFilter',
        ManagementPeriod: 'ManagementPeriodModel'
    ) -> Any:
        if filters.user_id is not None:
            query = query.where(ManagementPeriod.user_id == filters.user_id)

        if filters.start_date_max:
            start_date_max = self.__fix_time_zone(filters.start_date_max)
            query = query.where(ManagementPeriod.start_date < start_date_max)

        if filters.start_date_min:
            start_date_min = self.__fix_time_zone(filters.start_date_min)
            query = query.where(ManagementPeriod.start_date > start_date_min)

        if filters.end_date_max:
            end_date_max = self.__fix_time_zone(filters.end_date_max)
            query = query.where(ManagementPeriod.end_date < end_date_max)

        if filters.end_date_min:
            end_date_min = self.__fix_time_zone(filters.end_date_min)
            query = query.where(ManagementPeriod.end_date > end_date_min)

        if filters.order_stat_date:
            if filters.sort_order == 'desc':
                query = query.order_by(ManagementPeriod.start_date.desc())
            else:
                query = query.order_by(ManagementPeriod.start_date.asc())

        return query
    

    # TODO Extrair para um lugar comum
    def apply_pagination(
        self,
        query: Any,
        filters: 'ManagementPeriodFilter'
    ):
        size = filters.page_size
        page = filters.page
        query = query.limit(size).offset((page-1)*size)

        return query
    
    # TODO Extrair para um lugar comum
    def __fix_time_zone(self, dateTime: datetime) -> datetime:
        if dateTime.tzinfo is not None:
            dateTime = dateTime.astimezone(timezone.utc).replace(tzinfo=None)
        return dateTime