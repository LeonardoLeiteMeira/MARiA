from repository import UserLongTermMemoryRepository


class UserLongTermMemoryDomain:
    def __init__(self, repository: UserLongTermMemoryRepository) -> None:
        self.__repository = repository
        self.__max_memory_keys = 20

    async def get_user_memory(self, user_id: str) -> dict[str, str]:
        model = await self.__repository.get_by_user_id(user_id)
        if model is None:
            return {}
        return dict(model.memory_json)

    async def save_memory_patch(
        self, user_id: str, patch: dict[str, str]
    ) -> dict[str, str]:
        current_memory = await self.get_user_memory(user_id)
        updated_memory = {**current_memory, **patch}

        if len(updated_memory) > self.__max_memory_keys:
            raise ValueError(
                f"Long-term memory limit exceeded. Maximum allowed keys: {self.__max_memory_keys}."
            )

        saved = await self.__repository.upsert_user_memory(user_id, updated_memory)
        return dict(saved.memory_json)

    async def remove_memory_keys(self, user_id: str, keys: list[str]) -> dict[str, str]:
        current_memory = await self.get_user_memory(user_id)
        if not current_memory:
            return {}

        updated_memory = dict(current_memory)
        for key in keys:
            updated_memory.pop(key, None)

        saved = await self.__repository.upsert_user_memory(user_id, updated_memory)
        return dict(saved.memory_json)
