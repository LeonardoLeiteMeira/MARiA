from enum import Enum

class Database(Enum):
    TRANSACTIONS = "transactions"
    CATEGORIES = "categories"
    MONTHS = "months"
    CARDS = "cards"
    TYPES = "types"


# TODO 1  Criar estrutura que tenha a descricao do banco de dados
# Sera usado para que o agente possa identicar melhor a estrutura montada
# Talvez um agente que monte essa descrição?
# class Database:
#     database: DatabaseEnum
#     description: str
#     id: str