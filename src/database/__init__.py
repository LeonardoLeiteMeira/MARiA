from database.base_database import BaseDatabase
from database.repository.user_repository import UserRepository
import asyncio


async def test():
    database = BaseDatabase()
    repo = UserRepository(database)

    user = await repo.get_user_by_phone_number('5531933057272')
    print(user)
    await repo.create_user_new_thread(user.id)
    await repo._base_db.dispose()


if __name__ == '__main__':
    asyncio.run(test())