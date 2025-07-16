from external.notion.models.notion_base_database import NotionBaseDatabase
from external.notion.enum import NotionDatabaseEnum

class ChooseNotionDatabaseTagMixin:
    def select_database_tag(self, database: NotionBaseDatabase) -> NotionDatabaseEnum | None:
        match(database.name):
            case 'Gestões' | 'Meses':
                return NotionDatabaseEnum.MONTHS.value
            case 'Planejamento financeiro Gestão' | 'Planejamento mensal':
                return NotionDatabaseEnum.PLANNING.value
            case 'Transações':
                return NotionDatabaseEnum.TRANSACTIONS.value
            case 'Macro Categorias' | 'Uso do dinheiro':
                return NotionDatabaseEnum.MACRO_CATEGORIES.value
            case 'Contas/Cartões' | 'Contas, cartões e reservas':
                return NotionDatabaseEnum.CARDS.value
            case 'Áreas e Categorias' | 'Categorias':
                return NotionDatabaseEnum.CATEGORIES.value
            case _:
                return None