from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from typing import Optional, cast

from config import get_settings

class BaseDatabase:
    __instance: Optional['BaseDatabase'] = None

    def __new__(cls) -> 'BaseDatabase':
        if cls.__instance is None:
            db_instance = super(BaseDatabase, cls).__new__(cls)
            db_instance.__start_engine()
            db_instance.__start_session_maker()
            cls.__instance = db_instance

        return cls.__instance

    def __start_engine(self) -> None:
        settings = get_settings()
        database_conn_string = cast(str, settings.database_connection_uri_maria_async)

        self.engine = create_async_engine(
            database_conn_string,
            echo=settings.sqlalchemy_echo,
            pool_size=10,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=1800
        )

    def __start_session_maker(self) -> None:
        self.SessionMk = async_sessionmaker(self.engine, expire_on_commit=False)

    async def dispose(self) -> None:
        await self.engine.dispose()

    def session(self) -> AsyncSession:
        return self.SessionMk()
    
