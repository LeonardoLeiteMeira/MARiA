from .search_transactions import SearchTransactions
from .get_transactions_categories import GetTransactionsCategories
from .create_new_transaction import CreateNewTransaction
from .get_transaction_types import GetTransactionTypes
from .get_months import GetMonths
from .get_user_cards import GetUserCards
from .get_data_structure import GetDataStructure
from .get_all_databases import GeAllDatabases
from .get_month_planning import GetMonthPlanning
from .register_feedback_and_email import RegisterFeedbackAndEmail
from MARiA.memory import Database

tools = [
    SearchTransactions(), 
    GetTransactionsCategories(), 
    GetTransactionTypes(), 
    GetMonths(), 
    GetUserCards(), 
    CreateNewTransaction(), 
    GetDataStructure(), 
    GeAllDatabases(),
    GetMonthPlanning()
]

websummitTools = [
    RegisterFeedbackAndEmail(Database())
]