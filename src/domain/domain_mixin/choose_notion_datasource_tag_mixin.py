from external.notion.models.notion_base_datasource import NotionBaseDatasource
from external.notion.enum import NotionDatasourceEnum


class ChooseNotionDatasourceTagMixin:
    def select_datasource_tag(self, datasource: NotionBaseDatasource) -> str | None:
        match datasource.name:
            case "Gestões" | "Meses":
                return NotionDatasourceEnum.MONTHS.value
            case "Planejamento financeiro Gestão" | "Planejamento mensal":
                return NotionDatasourceEnum.PLANNING.value
            case "Transações":
                return NotionDatasourceEnum.TRANSACTIONS.value
            case "Macro Categorias" | "Uso do dinheiro":
                return NotionDatasourceEnum.MACRO_CATEGORIES.value
            case "Contas/Cartões" | "Contas, cartões e reservas":
                return NotionDatasourceEnum.CARDS.value
            case "Áreas e Categorias" | "Categorias":
                return NotionDatasourceEnum.CATEGORIES.value
            case _:
                return None
