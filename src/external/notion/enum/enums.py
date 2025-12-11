from enum import Enum

class NotionDatabaseEnum(Enum):
    TRANSACTIONS = "transactions"
    CATEGORIES = "categories"
    MONTHS = "months"
    CARDS = "cards"
    MACRO_CATEGORIES = "types"
    PLANNING = "planning"

class UserDataTypes(Enum):
    CATEGORIES = "categories"
    MACRO_CATEGORIES= "macroCategories"
    MONTHS = "months"
    CARDS_AND_ACCOUNTS = "cards"

# class NotionBaseColumns:
#     NotionDatabaseEnum.TRANSACTIONS = ['Nome', 'Valor', 'Data Planejada', 'Status', 'Categoria', 'Tipo de Transação', 'Entrada em', 'Saida de', 'Verificação', 'Macro Categorias']
#     NotionDatabaseEnum.CATEGORIES = ['Name']
#     NotionDatabaseEnum.MONTHS = ['Name', 'Data Inicio', 'Data Fim', 'Total Planejado', 'Gasto Concluido', 'Gasto Pendente', 'Gasto Total', 'Receitas recebida', ]

class TemplateTypes(str, Enum):
    SIMPLE_TEMPLATE = 'SIMPLE_TEMPLATE'
    EJ_FINANCE_TEMPLATE = 'EJ_FINANCE_TEMPLATE'
