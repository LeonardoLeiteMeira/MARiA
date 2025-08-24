from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..db_models.management_planning_model import ManagementPlanningModel
    from controllers.request_models.management_planning import ManagementPlanningFilter

class ManagementPlanningFilterToSqlAlchemyMixin:
    def apply_filters(
        self,
        query: Any,
        filters: 'ManagementPlanningFilter',
        ManagementPlanning: 'ManagementPlanningModel'
    ) -> Any:
        if filters.user_id is not None:
            query = query.where(ManagementPlanning.user_id == filters.user_id)

        if filters.management_period_id:
            query = query.where(ManagementPlanning.management_period_id.in_(filters.management_period_id))

        if filters.category_id:
            query = query.where(ManagementPlanning.category_id.in_(filters.category_id))

        if filters.name:
            query = query.where(ManagementPlanning.name.ilike(f"%{filters.name}%"))
        
        if filters.tags:
            query = query.where(ManagementPlanning.tags.in_(filters.tags))

        return query
    

    # TODO Extrair para um lugar comum
    def apply_pagination(
        self,
        query: Any,
        filters: 'ManagementPlanningFilter'
    ):
        size = filters.page_size
        page = filters.page
        query = query.limit(size).offset((page-1)*size)

        return query
