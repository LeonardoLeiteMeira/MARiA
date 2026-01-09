from .base_database import BaseDatabase
from .seed import seed_database, ensure_migrations
# from database.base_database import BaseDatabase
# from database.repository.user_repository import UserRepository
# import asyncio


# async def test():
#     database = BaseDatabase()
#     database1 = BaseDatabase()
#     database2 = BaseDatabase()
#     database3 = BaseDatabase()
    # repo = UserRepository(database)

    # user = await repo.get_user_last_thread_by_phone_number('5531933057272')
    # if not user:
    #     return
    
    # threads = await repo.get_user_last_thread_by_user_id(user.id)

    # if not threads:
    #     threads = [await repo.create_user_new_thread(user.id)]

    # if len(threads)>1:
    #     thread = threads[0]
    

    # await database.dispose()


# if __name__ == '__main__':
#     asyncio.run(test())

__all__ = ["BaseDatabase", "seed_database", "ensure_migrations"]
