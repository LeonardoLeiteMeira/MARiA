from database.base_database import BaseDatabase
from database.repository.user_repository import UserRepository
import asyncio


async def test():
    database = BaseDatabase()
    repo = UserRepository(database)

    thread = await repo.get_user_last_thread_by_phone_number('5531933057272')
    # cursor = await repo.get_user_with_last_thread('5531933057272')
    print(thread.thread_id)
    print(thread.status)




if __name__ == '__main__':
    asyncio.run(test())