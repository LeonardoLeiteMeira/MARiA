"""Database seeding utilities."""

from database.base_database import BaseDatabase
from sqlalchemy import text
import uuid
import subprocess
from config import get_settings
from alembic.config import Config
from alembic import command

DEFAULT_USER = {
    "name": "Leonardo Leite",
    "phone_number": "5531933057272",
    "email": "leonardo.leitemeira10@gmail.com",
}

async def seed_database(base_db: BaseDatabase) -> None:
    settings = get_settings()
    if not settings.is_production:
        return

    async with base_db.session() as session:
        query = text(
            "SELECT id FROM users WHERE phone_number = :phone_number LIMIT 1"
        )
        result = await session.execute(
            query, {"phone_number": DEFAULT_USER["phone_number"]}
        )
        if result.scalar_one_or_none():
            return

        insert_stmt = text(
            """
            INSERT INTO users (id, name, email, phone_number, created_at, updated_at)
            VALUES (:id, :name, :email, :phone_number, now(), now())
            """
        )
        await session.execute(
            insert_stmt,
            {
                "id": str(uuid.uuid4()),
                "name": DEFAULT_USER["name"],
                "email": DEFAULT_USER["email"],
                "phone_number": DEFAULT_USER["phone_number"],
            },
        )
        await session.commit()


async def ensure_migrations() -> None:
    settings = get_settings()
    if not settings.is_production:
        return
    
    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=True,
    )
