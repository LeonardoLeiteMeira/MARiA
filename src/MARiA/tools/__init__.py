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
from .search_data import SearchData
from .write_data import WriteData

tools_to_read_data = [
    SearchTransactions(), 
    GetTransactionsCategories(), 
    GetTransactionTypes(), 
    GetMonths(), 
    GetUserCards(), 
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