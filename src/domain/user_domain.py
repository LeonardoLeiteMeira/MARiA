from repository import UserRepository, ThreadModel, UserModel
from datetime import datetime, timedelta
import uuid

class UserDomain:
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository
        self.__valid_thread_period = (datetime.now()) - timedelta(hours=1)

    async def get_user_by_phone_number(self, phone_number:str) -> UserModel | None:
        return await self.__user_repository.get_user_by_phone_number(phone_number)
    
    async def get_user_valid_thread(self, user_id: str) -> list[ThreadModel]:
        return await self.__user_repository.get_user_valid_threads_by_user_id(user_id, self.__valid_thread_period)
    
    async def create_new_user_thread(self, user_id: str) -> ThreadModel:
        new_thread = ThreadModel(
            thread_id=uuid.uuid4(),
            user_id=user_id,
            status='open',
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now() - timedelta(hours=-3),
        )
        return await self.__user_repository.create_user_new_thread(new_thread)

