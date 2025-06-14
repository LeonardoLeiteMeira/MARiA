"""Database seeding utilities."""

from database.base_database import BaseDatabase
from sqlalchemy import text
import uuid

DEFAULT_USER = {
    "name": "Leonardo Leite",
    "phone_number": "5531933057272",
    "email": "leonardo.leitemeira10@gmail.com",
}

async def seed_database(base_db: BaseDatabase) -> None:
    """Create default user if it does not exist.

    This implementation relies solely on the ``database`` module, avoiding
    dependencies on ``repository`` or ``domain``.  It uses raw SQL through
    ``sqlalchemy`` to check for the user and insert it when missing.
    """

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
