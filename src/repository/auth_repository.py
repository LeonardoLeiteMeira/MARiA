from sqlalchemy import select
from uuid import UUID
from dto.models.user_dto import UserDto

from .base_repository import BaseRepository
from .db_models.user_model import UserModel
from .db_models.revoked_token_model import RevokedToken


class AuthRepository(BaseRepository):
    """Data access for authentication-related tables."""

    async def get_full_user_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        async with self.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first()

    async def get_base_user_by_email(self, email: str) -> UserDto | None:
        stmt = select(UserModel).where(UserModel.email == email)
        async with self.session() as session:
            res = await session.execute(stmt)
            full_user = res.scalars().first()
            return UserDto.model_validate(full_user)

    async def get_user_by_id(self, user_id: UUID) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        async with self.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first()

    async def create_user(self, user: UserModel) -> None:
        async with self.session() as session:
            session.add(user)
            await session.commit()

    async def save_user(self, user: UserModel) -> None:
        async with self.session() as session:
            session.add(user)
            await session.commit()

    # Revoked token operations
    async def add_revoked_token(self, token: RevokedToken) -> None:
        async with self.session() as session:
            session.add(token)
            await session.commit()

    async def is_token_revoked(self, jti: str) -> bool:
        stmt = select(RevokedToken).where(
            RevokedToken.jti == jti, RevokedToken.revoked_at.is_(None)
        )
        async with self.session() as session:
            res = await session.execute(stmt)
            return res.scalars().first() is not None
