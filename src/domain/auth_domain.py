from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session

from repository.auth_repository import AuthRepository
from repository.db_models.user_model import UserModel


class AuthDomain:
    """Business rules for authentication workflows."""

    def __init__(self, repo: AuthRepository):
        self._repo = repo

    def get_user_by_email(self, email: str) -> UserModel | None:
        return self._repo.get_user_by_email(email)

    def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        return self._repo.get_user_by_id(user_id)

    def create_user(self, name: str, email: str, password_hash: str) -> None:
        user = UserModel(name=name, email=email, phone_number=email, password=password_hash)
        self._repo.create_user(user)

    def save_user(self, user: UserModel) -> None:
        self._repo.save_user(user)

    def revoke_token(self, jti: str, expires: datetime) -> None:
        from repository.db_models.revoked_token_model import RevokedToken

        token = RevokedToken(jti=jti, expires=expires)
        self._repo.add_revoked_token(token)

    def is_token_revoked(self, jti: str) -> bool:
        return self._repo.is_token_revoked(jti)
