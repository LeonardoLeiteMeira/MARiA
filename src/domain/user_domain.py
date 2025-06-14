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
            id=uuid.uuid4(),
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now() - timedelta(hours=-3),
        )
        return await self.__user_repository.create_user_new_thread(new_thread)

    async def create_user(
        self,
        name: str,
        phone_number: str,
        email: str | None = None,
    ) -> UserModel:
        new_user = UserModel(
            id=uuid.uuid4(),
            name=name,
            email=email,
            phone_number=phone_number,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await self.__user_repository.create_user(new_user)
        return new_user

