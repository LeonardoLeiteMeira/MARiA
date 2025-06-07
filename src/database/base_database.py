import os
import dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

class BaseDatabase:
    __instance: 'BaseDatabase' = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(BaseDatabase, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        dotenv.load_dotenv()
        # Init da aplicação
        database_conn_string = os.getenv('DATABASE_CONNECTION_URI_MARIA_NEW')
        
        self.engine = create_async_engine(database_conn_string)
        self.SessionMk = async_sessionmaker(self.engine, expire_on_commit=False)

    async def dispose(self):
        await self.engine.dispose()

    def session(self) -> AsyncSession:
        """Return a new asynchronous session."""
        return self.SessionMk()
    
