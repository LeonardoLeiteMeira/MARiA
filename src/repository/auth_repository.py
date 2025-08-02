from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from .db_models.user_model import UserModel
from .db_models.revoked_token_model import RevokedToken


class AuthRepository:
    """Data access for authentication-related tables."""

    def __init__(self, db: Session):
        self._db = db

    # User operations
    def get_user_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create_user(self, user: UserModel) -> None:
        self._db.add(user)
        self._db.commit()

    def save_user(self, user: UserModel) -> None:
        self._db.add(user)
        self._db.commit()

    # Revoked token operations
    def add_revoked_token(self, token: RevokedToken) -> None:
        self._db.add(token)
        self._db.commit()

    def is_token_revoked(self, jti: str) -> bool:
        stmt = select(RevokedToken).where(
            RevokedToken.jti == jti, RevokedToken.revoked_at.is_(None)
        )
        return self._db.execute(stmt).scalar_one_or_none() is not None
