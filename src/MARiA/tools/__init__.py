from .search_transactions import SearchTransactions
from .get_transactions_categories import GetTransactionsCategories
from .create_new_transaction import CreateNewOutTransaction
from .get_transaction_types import GetTransactionTypes
from .get_months import GetMonths
from .get_user_cards import GetUserCards
from .get_data_structure import GetDataStructure
from .get_all_databases import GeAllDatabases
from .get_month_planning import GetMonthPlanning
from .register_feedback_and_email import RegisterFeedbackAndEmail
from .finished_test_period import FinishedTestPeriod
from .tool_agent.search_data import SearchData
from .tool_agent.write_data import WriteData

from .new_tools.tool_interface import ToolInterface
from .new_tools.create_card import CreateCard
from .new_tools.create_new_income import CreateNewIncome
from .new_tools.create_new_month import CreateNewMonth
from .new_tools.create_new_planning import CreateNewPlanning
from .new_tools.create_new_transaction_v2 import CreateNewOutTransactionV2
from .new_tools.create_new_transfer import CreateNewTransfer
from .new_tools.search_transactions_v2 import SearchTransactionV2
from .new_tools.read_user_base_data import ReadUserBaseData
from .new_tools.get_plan_by_month import GetPlanByMonth
from .new_tools.delete_data import DeleteData

tools_to_read_data = [
    SearchTransactions(), 
    # GetTransactionsCategories(), 
    # GetTransactionTypes(), 
    # GetMonths(),
    # GetUserCards(), 
    GetDataStructure(), 
    GeAllDatabases(),
    GetMonthPlanning()
]

tools_to_write_data = [
    CreateNewOutTransaction(), 
]

# websummitTools = [
#     RegisterFeedbackAndEmail(Database()),
#     FinishedTestPeriod(Database())
# ]