from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os
import dotenv

dotenv.load_dotenv()
def get_checkpointer_manager():
        database_conn_string = os.getenv('DATABASE_CONNECTION_URI_MARIA')
        return AsyncPostgresSaver.from_conn_string(database_conn_string)