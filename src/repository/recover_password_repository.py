from uuid import UUID

from sqlalchemy import delete, select

from .base_repository import BaseRepository
from .db_models.recover_password_model import RecoverPasswordModel


class RecoverPasswordRepository(BaseRepository):
    async def create(self, recover_password: RecoverPasswordModel) -> RecoverPasswordModel:
        async with self.session() as session:
            session.add(recover_password)
            await session.commit()
            await session.refresh(recover_password)
        return recover_password

    async def delete_by_user(self, user_id: UUID) -> None:
        stmt = delete(RecoverPasswordModel).where(RecoverPasswordModel.user_id == user_id)
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_by_user_and_code(
        self,
        user_id: UUID,
        code: str,
    ) -> RecoverPasswordModel | None:
        stmt = select(RecoverPasswordModel).where(
            RecoverPasswordModel.user_id == user_id,
            RecoverPasswordModel.code == code,
        )
        async with self.session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    async def delete(self, recover_password: RecoverPasswordModel) -> None:
        stmt = delete(RecoverPasswordModel).where(
            RecoverPasswordModel.id == recover_password.id
        )
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()
