from datetime import datetime, timedelta, timezone
import uuid
from uuid import UUID

from jose import jwt

from domain.auth_domain import AuthDomain
from app.core.security import (
    decode_token,
    hash_password,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_MINUTES,
)


class AuthApplication:
    """Application layer for user authentication."""

    def __init__(self, domain: AuthDomain):
        self._domain = domain

    async def signup(self, username: str, password: str) -> None:
        user = await self._domain.get_user_by_email(username)
        if not user:
            raise ValueError("User not registered")
        if user.password:
            raise ValueError("User already registered")
        user.password = hash_password(password)
        await self._domain.save_user(user)

    async def login(self, username: str, password: str) -> str:
        user = await self._domain.get_user_by_email(username)
        if not user or not verify_password(password, user.password):
            raise ValueError("Invalid credentials")
        return self._create_access_token(user)

    async def logout(self, token: str) -> None:
        payload = decode_token(token)
        expires = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        await self._domain.revoke_token(payload["jti"], expires)

    async def validate_token(self, token: str):
        payload = decode_token(token)
        if await self._domain.is_token_revoked(payload["jti"]):
            raise ValueError("Token revoked")
        user = await self._domain.get_user_by_id(UUID(payload["user_id"]))
        if not user:
            raise ValueError("User not found")
        return user

    def _create_access_token(self, user) -> str:
        to_encode = {
            "sub": user.email,
            "user_id": str(user.id),
            "jti": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
