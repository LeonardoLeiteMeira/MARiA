class NotionBaseDatasource:
    name: str = None
    id: str = None

    def __init__(self, name: str, id: str):
        self.name = name
        self.id = id
