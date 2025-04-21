import uuid
import dotenv
import os
from datetime import datetime
from psycopg_pool import AsyncConnectionPool
from typing import Optional

dotenv.load_dotenv()

# TODO quando tiver mais estrutura, mudar o self.pool.connection() para ser criado em nivel de request 
class Database:
    _instance: Optional["Database"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.database_conn_string = os.getenv('DATABASE_CONNECTION_URI_MARIA')
        self.pool = AsyncConnectionPool(
            conninfo=self.database_conn_string,
            max_size=10,
            kwargs={"autocommit": False},
            open=False,
        )
        
    async def start_connection(self):
        await self.pool.open()

    async def stop_connection(self):
        await self.pool.close()
    
    async def start_new_thread(self, user_id: str) -> str:
        new_thread = str(uuid.uuid4())
        await self.create_thread_record(thread_id=new_thread, user_id=user_id)
        return new_thread
    
    async def create_user(self, user_name: str, user_phone: str):
        async with self.pool.connection() as conn:
            try:
                query = (
                    "INSERT INTO users"
                    "(name, phone_number)"
                    "values (%s , %s);"
                )
                await conn.execute(query, (user_name, user_phone))
                await conn.commit()
            except Exception as ex:
                await conn.rollback()
                print(ex)
                raise ex

    async def create_thread_record(self, thread_id: str, user_id: str):
        async with self.pool.connection() as conn:
            try:
                now = datetime.now()
                query = (
                    "INSERT INTO threads"
                    "(thread_id, user_id, created_at)"
                    "values (%s , %s, %s);"
                )
                await conn.execute(query, (thread_id, user_id, now))
                await conn.commit()
            except Exception as ex:
                await conn.rollback()
                print(ex)
                raise ex

    async def get_user_by_phone_number(self, phone_number: str) -> dict | None:
        async with self.pool.connection() as conn:
            query = "SELECT * FROM users WHERE phone_number = $1"
            row = await conn.fetchrow(query, phone_number)
            return dict(row) if row else None
        
    async def get_thread_id_by_phone_number(self, phone_number: str) -> list | None:
        try:
            async with self.pool.connection() as conn:
                query = (
                    "SELECT u.id AS user_id, u.has_finished_test, "
                    "array_agg (t.thread_id ORDER BY t.created_at DESC) AS threads "
                    "FROM users u "
                    "LEFT JOIN threads t "
                    "ON u.id = t.user_id "
                    "WHERE u.phone_number = %s "
                    "GROUP BY u.id;"
                )
                cursor = await conn.execute(query, (phone_number,))
                row = await cursor.fetchone()
                if row is None:
                    return None
                columns = [col.name for col in cursor.description]
                dict_resp = dict(zip(columns, row))
                dict_resp['user_id'] = str(dict_resp['user_id'])
                dict_resp['threads'] = [str(thread_id) for thread_id in dict_resp['threads'] if thread_id is not None]
                return dict_resp
        except Exception as ex:
            print(ex)
            raise ex
        
    async def finish_user_feedback_by_thread_id(self, thread_id: str):
        try:
            async with self.pool.connection() as conn:
                query = (
                    "UPDATE users u "
                    "SET has_finished_test = TRUE "
                    "FROM threads t "
                    "WHERE t.thread_id = %s "
                    "AND t.user_id = u.id;"
                )
                await conn.execute(query, (thread_id,))
                await conn.commit()
        except Exception as ex:
            await conn.rollback()
            print(ex)
            raise ex


async def my_test():
    database = Database()
    await database.start_connection()
    result = await database.finish_user_feedback_by_thread_id("0b28b21a-41f8-43b3-8365-17bf8f153ff3")
    print(result)
    print("+++++++")

if __name__ == "__main__":
    import asyncio 
    asyncio.run(my_test())