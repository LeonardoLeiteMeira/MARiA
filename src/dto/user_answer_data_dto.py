from dataclasses import dataclass, field
from typing import List

from repository.db_models.notion_database_model import NotionDatabaseModel


@dataclass
class UserAnswerDataDTO:
    access_token: str
    use_default_template: bool
    user_databases: List[NotionDatabaseModel] = field(default_factory=list)