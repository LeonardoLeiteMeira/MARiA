from enum import Enum

class NotionDatabaseEnum(Enum):
    TRANSACTIONS = "transactions"
    CATEGORIES = "categories"
    MONTHS = "months"
    CARDS = "cards"
    TYPES = "types"
    PLANNING = "planning"

# class NotionBaseColumns:
#     NotionDatabaseEnum.TRANSACTIONS = ['Nome', 'Valor', 'Data Planejada', 'Status', 'Categoria', 'Tipo de Transação', 'Entrada em', 'Saida de', 'Verificação', 'Macro Categorias']
#     NotionDatabaseEnum.CATEGORIES = ['Name']
#     NotionDatabaseEnum.MONTHS = ['Name', 'Data Inicio', 'Data Fim', 'Total Planejado', 'Gasto Concluido', 'Gasto Pendente', 'Gasto Total', 'Receitas recebida', ]