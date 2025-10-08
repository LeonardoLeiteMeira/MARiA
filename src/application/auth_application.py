from datetime import datetime, timedelta, timezone
import secrets
import uuid
from uuid import UUID
from jose import jwt

from dto.models.user_dto import UserDto
from dto.models.auth_user_dto import AuthUserDto
from domain.auth_domain import AuthDomain
from domain.recover_password_domain import RecoverPasswordDomain
from app.core.security import (
    decode_token,
    hash_password,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_MINUTES,
)
from messaging import MessageService


class AuthApplication:
    def __init__(
        self,
        domain: AuthDomain,
        message_service: MessageService,
        recover_password_domain: RecoverPasswordDomain,
    ):
        self._domain = domain
        self.__mensage_service = message_service
        self._recover_password_domain = recover_password_domain

    async def signup(self, username: str, password: str) -> None:
        user = await self._domain.get_full_user_by_email(username)
        if not user:
            raise ValueError("User not registered")
        if user.password:
            raise ValueError("User already registered")
        user.password = hash_password(password)
        await self._domain.save_user(user)

    async def login(self, username: str, password: str) -> AuthUserDto:
        user = await self._domain.get_full_user_by_email(username)
        if not user or not verify_password(password, user.password):
            raise ValueError("Invalid credentials")
        token = self._create_access_token(user)
        return AuthUserDto(
            user=UserDto.model_validate(user),
            token_type='bearer',
            access_token=token
        )

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
    
    async def get_recover_code(self, user_email: str) -> None:
        user = await self._domain.get_full_user_by_email(user_email)
        if not user:
            raise ValueError("User not found")
        if not user.phone_number:
            raise ValueError("User phone number not available")

        code = f"{secrets.randbelow(1_000_000):06d}"
        limit_date = datetime.now(timezone.utc) + timedelta(minutes=15)

        await self._recover_password_domain.create_code(
            user_id=user.id,
            code=code,
            limit_date=limit_date,
        )

        message = (
            "Seu código de recuperação de senha é "
            f"{code}. Ele expira em 15 minutos."
        )
        await self.__mensage_service.send_message(
            chat_id=user.phone_number,
            message=message,
        )

    async def update_password_by_code(self, user_email: str, code: str, new_password: str):
        user = await self._domain.get_full_user_by_email(user_email)
        if not user:
            raise ValueError("User not found")

        recover_password = await self._recover_password_domain.get_code(user.id, code)
        if not recover_password:
            raise ValueError("Invalid recovery code")

        limit_date = recover_password.limit_date
        if limit_date.tzinfo is None:
            limit_date = limit_date.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if limit_date < now:
            await self._recover_password_domain.consume_code(recover_password)
            raise ValueError("Recovery code expired")

        user.password = hash_password(new_password)
        await self._domain.save_user(user)
        await self._recover_password_domain.consume_code(recover_password)
