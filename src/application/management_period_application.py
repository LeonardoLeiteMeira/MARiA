from uuid import UUID
from typing import TYPE_CHECKING, Dict, List

from domain import (
    ManagementPeriodDomain,
    ManagementPlanningDomain,
    CategoryDomain,
    TransactionDomain
)
from dto.models.transaction_dto import TransactionType
from repository import ManagementPeriodModel, CategoryModel
from dto import PaginatedDataListDto
from dto.models import ManagementPeriodDto, ManagementPlanningDto, TransactionDto
from dto.aggregates import DashboardAggregate, PlanningAggregate, CategoryTransactionAggregate

from controllers.request_models.management_period import ManagementPeriodFilter
from controllers.request_models.management_planning import ManagementPlanningFilter
from controllers.request_models.transaction import TransactionFilter

if TYPE_CHECKING:
    from controllers.request_models.management_period import ManagementPeriodRequest


class ManagementPeriodApplication:
    """Application layer for management period.

    All business validations should be placed here before delegating to the
    domain layer. For now it simply forwards the calls."""

    def __init__(
            self,
            domain: ManagementPeriodDomain,
            plannig_domain: ManagementPlanningDomain,
            category_domain: CategoryDomain,
            transaction_domain: TransactionDomain, 
        ):
            self._domain = domain
            self.plannig_domain = plannig_domain
            self.category_domain = category_domain
            self.transaction_domain = transaction_domain

    async def create(self, data: "ManagementPeriodRequest") -> ManagementPeriodModel:
        period = ManagementPeriodModel(**(data.model_dump()))
        return await self._domain.create(period)

    async def update(self, period_id: UUID, data: "ManagementPeriodRequest") -> ManagementPeriodModel:
        period =  ManagementPeriodModel(**(data.model_dump()))
        period.id = period_id
        return await self._domain.update(period)

    async def delete(self, period_id: UUID, user_id: UUID) -> None:
        await self._domain.delete(period_id, user_id)

    async def get_by_ids(self, period_ids: list[UUID]) -> list[ManagementPeriodModel]:
        return await self._domain.get_by_ids(period_ids)

    async def get_by_filter(self, filter: 'ManagementPeriodFilter') -> PaginatedDataListDto[ManagementPeriodDto]:
        return await self._domain.get_by_filter(filter)

    async def get_current_period_resume(self, user_id: UUID):
        current_period = await self.get_current_management_period(user_id)
        plans = await self.__get_management_plan(user_id, current_period.id)
        categories = await self.category_domain.get_by_user_id(user_id)
        transactions = await self.__get_period_transactions(user_id, current_period.id)

        categories_by_id: Dict[str, CategoryModel] = {}
        for cat in categories:
            categories_by_id[str(cat.id)] = cat

        plans_by_category: Dict[str, ManagementPlanningDto] = {}
        for plan in plans:
            plans_by_category[str(plan.category_id)] = plan

        # Total de entradas
        all_incomes = [transaction for transaction in transactions if transaction.type == TransactionType.INCOME]
        total_incomes = sum(income.amount_cents for income in all_incomes)

        # Total de saidas (Gastos)
        all_expenses = [transaction for transaction in transactions if transaction.type == TransactionType.EXPENSE]
        total_expense = sum(expense.amount_cents for expense in all_expenses)

        # Total Planjeado
        total_plan = sum(plan.planned_value_cents for plan in plans)

        # Disponivel para planejar
        available_to_plan = total_incomes - total_plan

        # Total gasto em cada categoria
        expenses_by_category: Dict[str, CategoryTransactionAggregate] = {}
        for expense in all_expenses:
            key = str(expense.category_id)
            if not (key in expenses_by_category):
                category = categories_by_id[key]
                plan = plans_by_category.get(key, None)
                aggregate = CategoryTransactionAggregate(
                    category_id = expense.category_id,
                    total =  0,
                    transactions =  [],
                    category_name =  category.name,
                    icon =  category.icon,
                    plan_value =  plan.planned_value_cents if plan!=None else None,
                    plan_name =  plan.name if plan!=None else None,
                )
                expenses_by_category[key] = aggregate

            expenses_by_category[key].transactions.append(expense)
            expenses_by_category[key].total += expense.amount_cents

        # Total gasto de cada planejamento
        plan_aggregate: List[PlanningAggregate] = []
        for plan in plans:

            expense_data = expenses_by_category.get(str(plan.category_id), None)
            total_expenses_plan = expense_data['total'] if expense_data != None else 0

            new_plan = PlanningAggregate(
                plan_id = plan.id,
                category_id = plan.category_id,
                plan_value_cents = plan.planned_value_cents,
                total_expenses = total_expenses_plan,
                total_available = plan.planned_value_cents - total_expenses_plan,
                name = plan.name,
                category_name = expense_data['category_name'] if expense_data != None else None,
                category_icon =  expense_data['category_icon'] if expense_data != None else None,
                transactions = expense_data['transactions'] if expense_data != None else [],
            )

            plan_aggregate.append(new_plan)
            

        # Lista de Transacoes fora do planejamento
        plan_categories = set([str(plan.category_id) for plan in plans])
        transactions_without_plan = [expense for expense in all_expenses if str(expense.category_id) not in plan_categories]

        # Total fora do planejamento
        total_expenses_out_plan = sum(expense.amount_cents for expense in transactions_without_plan)

        final_dashboard = DashboardAggregate(
            start_period = current_period.start_date,
            end_period = current_period.end_date,
            total_incomes = total_incomes,
            total_expense = total_expense,
            total_plan = total_plan,
            available_to_plan = available_to_plan,
            total_expenses_out_plan = total_expenses_out_plan,
            planning_aggregate = plan_aggregate,
        )

        print(final_dashboard)



    async def get_current_management_period(self, user_id: UUID) -> ManagementPeriodDto:
        management_filter = ManagementPeriodFilter(
            page=1,
            page_size=1,
            order_start_date='desc',
            user_id=user_id
        )
        management_result = await self._domain.get_by_filter(management_filter)
        if len(management_result.list_data) == 0:
            raise "There is no management period to read"
        
        return management_result.list_data[0]
    
    async def __get_management_plan(self, user_id:UUID, period_plan_id:UUID) -> list[ManagementPlanningDto]:
        plan_filter = ManagementPlanningFilter(
            management_period_id=[period_plan_id],
            page_size=200,
            user_id=user_id
        )
        plan_result = await self.plannig_domain.get_by_user_id(plan_filter)
        return plan_result.list_data
    
    async def __get_period_transactions(self, user_id:UUID, period_id: UUID) -> list[TransactionDto]:
        transaction_filter = TransactionFilter(
            management_period_id=[period_id],
            user_id=user_id,
            page_size=2000
        )
        transactions_result = await self.transaction_domain.get_user_transactions_with_filter(transaction_filter)
        return transactions_result.list_data