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
            db_instance = super(BaseDatabase, cls).__new__(cls)
            db_instance._BaseDatabase__start_engine()
            db_instance._BaseDatabase__start_session_maker()
            cls.__instance = db_instance

        return cls.__instance

    def __start_engine(self):
        dotenv.load_dotenv()
        database_conn_string = os.getenv('DATABASE_CONNECTION_URI_MARIA_NEW')

        self.engine = create_async_engine(
            database_conn_string,
            echo=True,
            pool_size=10,
            max_overflow=0,
        )

    def __start_session_maker(self):
        self.SessionMk = async_sessionmaker(self.engine, expire_on_commit=False)

    async def dispose(self):
        await self.engine.dispose()

    def session(self) -> AsyncSession:
        return self.SessionMk()
    
