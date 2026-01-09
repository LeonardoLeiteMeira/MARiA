from typing import Optional


class NotionBaseDatasource:
    name: Optional[str] = None
    id: Optional[str] = None

    def __init__(self, name: str, id: str) -> None:
        self.name = name
        self.id = id
