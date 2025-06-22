from contextlib import _AsyncGeneratorContextManager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from config import get_settings


def get_checkpointer_manager() -> _AsyncGeneratorContextManager[AsyncPostgresSaver]:
    settings = get_settings()
    database_conn_string = settings.database_connection_uri_maria
    return AsyncPostgresSaver.from_conn_string(database_conn_string)
