import uuid
import dotenv
import os
from datetime import datetime
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

dotenv.load_dotenv()

class Database:
    def __init__(self):
        connection_string = os.getenv('DATABASE_CONNECTION_URI')
        databse_uri = f"{connection_string}/maria"
        self.pool = AsyncConnectionPool(
            conninfo=databse_uri,
            max_size=10,
            kwargs={"autocommit": True},
        )

    async def init_checkpointer(self) -> AsyncPostgresSaver:
        checkpointer = AsyncPostgresSaver(self.pool)
        await checkpointer.setup()  
        return checkpointer
    
    async def start_new_thread(self, user_id: str) -> str:
        new_thread = str(uuid.uuid4())
        await self.create_thread_record(thread_id=new_thread, user_id=user_id)
        return new_thread
    
    
    async def create_thread_record(self, thread_id: str, user_id: str):
        now = datetime.now()
        query = (
            f"INSERT INTO threads"
            f"(thread_id, user_id, created_at)"
            f"values ($1, $2, $3);"
        )
        async with self.pool.connection as conn:
            await conn.execute(query, thread_id, user_id, now)

    async def get_user_by_phone_number(self, phone_number: str) -> dict | None:
        async with self.pool.connection() as conn:
            query = "SELECT * FROM users WHERE phone_number = $1"
            row = await conn.fetchrow(query, phone_number)
            return dict(row) if row else None
        
    async def get_thread_id_by_phone_number(self, phone_number: str) -> list | None:
        async with self.pool.connection() as conn:
            query = (
                "SELECT t.thread_id, u.id "
                "FROM threads t "
                "JOIN users u ON t.user_id = u.id "
                "WHERE u.phone_number = $1"
                "ORDER BY t.created_at DESC;"
            )
            results = await conn.fetch(query, phone_number)
            return [dict(row) for row in results]
