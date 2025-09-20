from datetime import datetime
from uuid import UUID

from dto.models.user_dto import UserDto

from repository.auth_repository import AuthRepository
from repository.db_models.user_model import UserModel


class AuthDomain:
    """Business rules for authentication workflows."""

    def __init__(self, repo: AuthRepository):
        self._repo = repo

    async def get_full_user_by_email(self, email: str) -> UserModel | None:
        return await self._repo.get_full_user_by_email(email)
    
    async def get_base_user_by_email(self, email: str) -> UserDto | None:
        return await self._repo.get_base_user_by_email(email)

    async def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        return await self._repo.get_user_by_id(user_id)

    async def create_user(self, name: str, email: str, password_hash: str) -> None:
        user = UserModel(name=name, email=email, phone_number=email, password=password_hash)
        await self._repo.create_user(user)

    async def save_user(self, user: UserModel) -> None:
        await self._repo.save_user(user)

    async def revoke_token(self, jti: str, expires: datetime) -> None:
        from repository.db_models.revoked_token_model import RevokedToken

        token = RevokedToken(jti=jti, expires=expires)
        await self._repo.add_revoked_token(token)

    async def is_token_revoked(self, jti: str) -> bool:
        return await self._repo.is_token_revoked(jti)
