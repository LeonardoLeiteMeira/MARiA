from datetime import datetime
from uuid import UUID

from repository import RecoverPasswordRepository, RecoverPasswordModel


class RecoverPasswordDomain:
    def __init__(self, repo: RecoverPasswordRepository):
        self._repo = repo

    async def create_code(
        self, user_id: UUID, code: str, limit_date: datetime
    ) -> RecoverPasswordModel:
        await self._repo.delete_by_user(user_id)
        recover_password = RecoverPasswordModel(
            user_id=user_id,
            code=code,
            limit_date=limit_date,
        )
        return await self._repo.create(recover_password)

    async def get_code(self, user_id: UUID, code: str) -> RecoverPasswordModel | None:
        return await self._repo.get_by_user_and_code(user_id, code)

    async def consume_code(self, recover_password: RecoverPasswordModel) -> None:
        await self._repo.delete(recover_password)
