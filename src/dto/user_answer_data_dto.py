from dataclasses import dataclass, field
from typing import List

from repository.db_models.notion_datasource_model import NotionDatasourceModel


@dataclass
class UserAnswerDataDTO:
    access_token: str
    use_default_template: bool
    user_datasources: List[NotionDatasourceModel] = field(default_factory=list)
